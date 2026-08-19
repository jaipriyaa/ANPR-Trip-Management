import logging
import os
import time
import cv2
import numpy as np
from typing import List, Dict, Optional, Tuple

from app.ai import config
from app.ai.utils.bbox_utils import scale_bbox, clip_bbox, non_max_suppression, pad_bbox

logger = logging.getLogger(__name__)


from app.ai.inference.backend_selector import BackendSelector


class VehicleDetector:
    """
    Enterprise Edge Vehicle Detector using TensorRT / ONNX / PyTorch with CPU & GPU support.
    Detects Cars, SUVs, Pickup Trucks, Heavy Trucks, Mini Trucks, Buses, Vans, Motorcycles, Auto Rickshaws.
    """

    def __init__(self):
        self._model_trt = None
        self._model_onnx = None
        self._model_pt = None
        self._input_size = config.VEHICLE_IMGSZ
        self._conf_threshold = config.VEHICLE_CONF_THRESHOLD
        self._iou_threshold = config.VEHICLE_IOU_THRESHOLD
        self._coco_classes = config.COCO_VEHICLE_CLASSES
        self.selector = BackendSelector(
            engine_path=config.VEHICLE_DETECTION_MODEL_ENGINE,
            onnx_path=config.VEHICLE_DETECTION_MODEL_ONNX,
            pt_path=config.VEHICLE_DETECTION_MODEL_PT,
            model_name="Vehicle Detector",
        )

    def _load(self):
        """Model Loader: Resolves active backend (TensorRT -> ONNX -> PyTorch) and loads session."""
        if self._model_trt is not None or self._model_onnx is not None or self._model_pt is not None:
            return

        chosen_backend = self.selector.resolve_backend()

        if chosen_backend == "TENSORRT":
            try:
                import onnxruntime as ort
                providers = ["TensorrtExecutionProvider", "CUDAExecutionProvider", "CPUExecutionProvider"]
                avail_providers = [p for p in providers if p in ort.get_available_providers()]
                self._model_trt = ort.InferenceSession(
                    config.VEHICLE_DETECTION_MODEL_ENGINE if os.path.exists(config.VEHICLE_DETECTION_MODEL_ENGINE) else config.VEHICLE_DETECTION_MODEL_ONNX,
                    providers=avail_providers,
                )
                logger.info(f"Vehicle detector TensorRT session loaded with providers: {avail_providers}")
                return
            except Exception as e:
                logger.warning(f"TensorRT load failed: {e}. Falling back to ONNX.")
                chosen_backend = "ONNX"

        # Prioritize PyTorch YOLO model if present
        if os.path.exists(config.VEHICLE_DETECTION_MODEL_PT):
            try:
                from ultralytics import YOLO
                model_path = config.VEHICLE_DETECTION_MODEL_PT
                self._model_pt = YOLO(model_path)
                model_names = getattr(self._model_pt, "names", self._coco_classes)
                logger.info(f"ACTIVE VEHICLE MODEL (PyTorch YOLO): Path: {model_path}, Class Names: {model_names}")
                return
            except Exception as e:
                logger.warning(f"Failed to load PyTorch YOLO vehicle detector: {e}")

        if chosen_backend == "ONNX":
            if os.path.exists(config.VEHICLE_DETECTION_MODEL_ONNX):
                try:
                    import onnxruntime as ort
                    providers = ["CUDAExecutionProvider", "CPUExecutionProvider"] if config.GPU_ENABLED else ["CPUExecutionProvider"]
                    avail_providers = [p for p in providers if p in ort.get_available_providers()]
                    if not avail_providers:
                        avail_providers = ort.get_available_providers()
                    self._model_onnx = ort.InferenceSession(
                        config.VEHICLE_DETECTION_MODEL_ONNX,
                        providers=avail_providers,
                    )
                    logger.info(f"ACTIVE VEHICLE MODEL (ONNX): {config.VEHICLE_DETECTION_MODEL_ONNX} with providers {avail_providers}")
                    return
                except Exception as e:
                    logger.warning(f"ONNX vehicle detector load failed: {e}. Falling back to PyTorch YOLO.")
                    chosen_backend = "PYTORCH"

    def _classify_sub_type(self, base_label: str, bbox: List[int], img_shape: Tuple[int, int]) -> str:
        """Fine-grained classification mapping COCO classes & model names strictly to Car, Truck, Bus, Motorcycle."""
        label_lower = (base_label or "").lower()

        if "truck" in label_lower:
            return "Truck"
        elif "bus" in label_lower:
            return "Bus"
        elif "motorcycle" in label_lower or "rickshaw" in label_lower or "bike" in label_lower:
            return "Motorcycle"
        elif "car" in label_lower or "suv" in label_lower or "van" in label_lower:
            return "Car"
        
        return "Unknown"



    def _preprocess(self, image: np.ndarray) -> Tuple[np.ndarray, float, int, int]:
        """Preprocessing step: letterbox resizing and canvas padding."""
        h, w = image.shape[:2]
        target_w, target_h = self._input_size
        scale = min(target_w / max(w, 1), target_h / max(h, 1))
        nw, nh = int(w * scale), int(h * scale)
        resized = cv2.resize(image, (nw, nh), interpolation=cv2.INTER_LINEAR)

        canvas = np.full((target_h, target_w, 3), 114, dtype=np.uint8)
        dx = (target_w - nw) // 2
        dy = (target_h - nh) // 2
        canvas[dy:dy + nh, dx:dx + nw] = resized

        return canvas, scale, dx, dy

    def _run_inference(self, canvas: np.ndarray):
        """Inference execution abstraction layer."""
        if self._model_pt is not None:
            import torch
            device = getattr(config, "GPU_DEVICE", 0) if (getattr(config, "GPU_ENABLED", True) and torch.cuda.is_available()) else "cpu"
            results = self._model_pt(
                canvas,
                conf=self._conf_threshold,
                iou=self._iou_threshold,
                classes=list(self._coco_classes.keys()),
                device=device,
                verbose=False,
            )
            return ("pt", results)

        elif self._model_onnx is not None:
            blob = np.transpose(canvas, (2, 0, 1)).astype(np.float32) / 255.0
            blob = np.expand_dims(blob, axis=0)
            input_name = self._model_onnx.get_inputs()[0].name
            raw_output = self._model_onnx.run(None, {input_name: blob})[0]
            return ("onnx", raw_output)

        raise RuntimeError("No loaded inference backend available.")

    def _postprocess(self, inference_result, scale: float, dx: int, dy: int, orig_shape: Tuple[int, int]) -> List[dict]:
        """Postprocessing step: parsing raw model tensors, coordinate scaling, NMS, and sub-type classification."""
        backend_type, raw_data = inference_result
        orig_h, orig_w = orig_shape
        predictions = []

        if backend_type == "pt":
            results = raw_data
            if len(results) > 0 and hasattr(results[0], "boxes"):
                for box in results[0].boxes:
                    bx1, by1, bx2, by2 = map(int, box.xyxy[0].tolist())
                    conf = float(box.conf[0])
                    cls_id = int(box.cls[0])
                    names_dict = getattr(self._model_pt, "names", {}) if hasattr(self, "_model_pt") and self._model_pt else {}
                    base_label = names_dict.get(cls_id, self._coco_classes.get(cls_id, "Unknown"))

                    scaled_box = scale_bbox([bx1, by1, bx2, by2], scale, dx, dy, (orig_h, orig_w))
                    vehicle_type = self._classify_sub_type(base_label, scaled_box, (orig_h, orig_w))

                    logger.info(f"RAW YOLO DETECTION: class_id={cls_id}, class_name={base_label}, confidence={conf:.4f}, bbox={scaled_box}, FINAL vehicle_type={vehicle_type}")



                    predictions.append({
                        "vehicle_bbox": scaled_box,
                        "vehicle_confidence": round(conf, 4),
                        "vehicle_type": vehicle_type,
                        "class_id": cls_id,
                        "base_label": base_label,
                        "width": scaled_box[2] - scaled_box[0],
                        "height": scaled_box[3] - scaled_box[1],
                    })


        elif backend_type == "onnx":
            output = raw_data[0]
            if output.shape[0] < output.shape[1]:
                output = output.T

            for row in output:
                class_probs = row[4:]
                if len(class_probs) == 0:
                    continue

                cls_id = int(np.argmax(class_probs))
                conf = float(class_probs[cls_id])

                if conf < self._conf_threshold:
                    continue

                if cls_id not in self._coco_classes:
                    continue


                cx, cy, bw, bh = row[:4]
                bx1 = int(cx - bw / 2)
                by1 = int(cy - bh / 2)
                bx2 = int(cx + bw / 2)
                by2 = int(cy + bh / 2)

                scaled_box = scale_bbox([bx1, by1, bx2, by2], scale, dx, dy, (orig_h, orig_w))
                base_label = self._coco_classes[cls_id]
                vehicle_type = self._classify_sub_type(base_label, scaled_box, (orig_h, orig_w))

                predictions.append({
                    "vehicle_bbox": scaled_box,
                    "vehicle_confidence": round(conf, 4),
                    "vehicle_type": vehicle_type,
                    "class_id": cls_id,
                    "base_label": base_label,
                    "width": scaled_box[2] - scaled_box[0],
                    "height": scaled_box[3] - scaled_box[1],
                })

            predictions = non_max_suppression(predictions, iou_threshold=self._iou_threshold)

        return predictions

    def detect(self, image: np.ndarray) -> dict:
        """Main detection entry point orchestrating Load -> Preprocess -> Inference -> Postprocess."""
        start_time = time.time()
        self._conf_threshold = config.VEHICLE_CONF_THRESHOLD
        self._iou_threshold = config.VEHICLE_IOU_THRESHOLD
        self._input_size = config.VEHICLE_IMGSZ
        self._load()

        if image is None or image.size == 0:
            return {
                "vehicles": [],
                "best_vehicle": None,
                "vehicle_count": 0,
                "processing_time_ms": 0.0,
                "image_size": (0, 0),
            }

        orig_h, orig_w = image.shape[:2]
        canvas, scale, dx, dy = self._preprocess(image)
        raw_inference = self._run_inference(canvas)
        predictions = self._postprocess(raw_inference, scale, dx, dy, (orig_h, orig_w))

        # COCO model ensemble verification / fallback to resolve weak custom model classification ambiguity or 0 detections
        if os.path.exists(config.ROOT_YOLO11_PT):
            try:
                if not hasattr(self, "_coco_model") or self._coco_model is None:
                    from ultralytics import YOLO
                    self._coco_model = YOLO(config.ROOT_YOLO11_PT)

                import torch
                device = getattr(config, "GPU_DEVICE", 0) if (getattr(config, "GPU_ENABLED", True) and torch.cuda.is_available()) else "cpu"
                coco_res = self._coco_model(image, conf=0.25, classes=[2, 3, 5, 7], device=device, verbose=False)[0]
                if len(coco_res.boxes) > 0:
                    c_name_map = {2: "Car", 3: "Motorcycle", 5: "Bus", 7: "Truck"}
                    c_cls_map = {2: 0, 3: 1, 5: 2, 7: 3}
                    c_label_map = {2: "car", 3: "motorcycle", 5: "bus", 7: "truck"}

                    if not predictions:
                        for box in coco_res.boxes:
                            bx1, by1, bx2, by2 = map(int, box.xyxy[0].tolist())
                            c_conf = float(box.conf[0])
                            c_cls = int(box.cls[0])
                            c_type = c_name_map.get(c_cls, "Car")
                            c_label = c_label_map.get(c_cls, "car")
                            c_cid = c_cls_map.get(c_cls, 0)

                            predictions.append({
                                "vehicle_bbox": [bx1, by1, bx2, by2],
                                "vehicle_confidence": round(c_conf, 4),
                                "vehicle_type": c_type,
                                "class_id": c_cid,
                                "base_label": c_label,
                                "width": bx2 - bx1,
                                "height": by2 - by1,
                            })
                    else:
                        c_box = coco_res.boxes[0]
                        c_conf = float(c_box.conf[0])
                        c_cls = int(c_box.cls[0])
                        c_type = c_name_map.get(c_cls, "Car")

                        for pred in predictions:
                            if pred["vehicle_type"] == "Truck" and pred["vehicle_confidence"] < 0.60 and c_type == "Car" and c_conf > 0.70:
                                logger.info(f"ENSEMBLE CORRECTION: Overriding Truck (conf={pred['vehicle_confidence']:.2f}) -> Car (conf={c_conf:.2f})")
                                pred["vehicle_type"] = "Car"
                                pred["base_label"] = "car"
                                pred["class_id"] = 0
                                pred["vehicle_confidence"] = round(c_conf, 4)
            except Exception as e:
                logger.warning(f"COCO ensemble check error: {e}")

        best_vehicle = None
        if predictions:
            best_vehicle = max(predictions, key=lambda p: p["width"] * p["height"])

        elapsed_ms = round((time.time() - start_time) * 1000, 2)
        return {
            "vehicles": predictions,
            "best_vehicle": best_vehicle,
            "vehicle_count": len(predictions),
            "processing_time_ms": elapsed_ms,
            "image_size": (orig_w, orig_h),
        }


def crop_vehicle(image: np.ndarray, bbox: List[int], pad_pct: float = 0.02) -> np.ndarray:
    """Crops vehicle ROI from image with safety padding."""
    if image is None or len(bbox) != 4:
        return np.array([])
    padded_box = pad_bbox(bbox, image.shape[:2], margin_pct=pad_pct)
    x1, y1, x2, y2 = padded_box
    return image[y1:y2, x1:x2].copy()
