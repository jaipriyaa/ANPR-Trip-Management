import logging
import os
import time
import cv2
import numpy as np
from typing import List, Optional

from app.ai import config

logger = logging.getLogger(__name__)


class VehicleDetector:
    def __init__(self):
        self._model = None
        self._model_pt = None
        self._input_size = config.VEHICLE_IMGSZ
        self._conf_threshold = config.VEHICLE_CONF_THRESHOLD
        self._iou_threshold = config.VEHICLE_IOU_THRESHOLD
        self._class_names = getattr(config, "VEHICLE_CLASSES", config.COCO_VEHICLE_CLASSES)

    def _load(self):
        if self._model is not None or self._model_pt is not None:
            return

        backend = getattr(config, "MODEL_BACKEND", "PYTORCH")
        if backend == "TENSORRT":
            raise NotImplementedError("TensorRT backend is not yet supported in Phase 12.1. Use ONNX or PYTORCH.")

        if backend == "ONNX" or (getattr(config, "ENABLE_ONNX", True) and os.path.exists(config.VEHICLE_DETECTION_MODEL_ONNX)):
            onnx_path = getattr(config, "VEHICLE_DETECTION_MODEL_ONNX", os.path.join(config.MODEL_DIR, "vehicle_detector.onnx"))
            if os.path.exists(onnx_path):
                try:
                    import onnxruntime as ort
                    providers = ["CUDAExecutionProvider", "CPUExecutionProvider"] if getattr(config, "GPU_ENABLED", True) else ["CPUExecutionProvider"]
                    avail_providers = [p for p in providers if p in ort.get_available_providers()]
                    if not avail_providers:
                        avail_providers = ort.get_available_providers()
                    self._model = ort.InferenceSession(onnx_path, providers=avail_providers)
                    logger.info(f"Vehicle detector ONNX loaded ({len(avail_providers)} providers)")
                    return
                except Exception as e:
                    logger.warning(f"ONNX load failed, falling back to PyTorch: {e}")

        from ultralytics import YOLO
        self._model_pt = YOLO(config.VEHICLE_DETECTION_MODEL_PT)
        logger.info(f"Vehicle detector YOLO loaded: {config.VEHICLE_DETECTION_MODEL_PT}")

    def _preprocess(self, image: np.ndarray) -> np.ndarray:
        h, w = image.shape[:2]
        target_w, target_h = self._input_size
        scale = min(target_w / max(w, 1), target_h / max(h, 1))
        nw, nh = int(w * scale), int(h * scale)
        resized = cv2.resize(image, (nw, nh), interpolation=cv2.INTER_LINEAR)

        canvas = np.full((target_h, target_w, 3), 114, dtype=np.uint8)
        dx = (target_w - nw) // 2
        dy = (target_h - nh) // 2
        canvas[dy:dy + nh, dx:dx + nw] = resized

        self._scale = scale
        self._dx = dx
        self._dy = dy
        return canvas

    def _postprocess(self, preds, image_shape) -> list:
        h, w = image_shape[:2]
        scale = self._scale
        dx = self._dx
        dy = self._dy
        boxes = []

        if hasattr(preds, "boxes"):
            for box in preds.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                conf = float(box.conf[0])
                cls_id = int(box.cls[0])
                label = self._class_names.get(cls_id, "vehicle")

                ox1 = int((x1 - dx) / scale)
                oy1 = int((y1 - dy) / scale)
                ox2 = int((x2 - dx) / scale)
                oy2 = int((y2 - dy) / scale)
                ox1 = max(0, ox1); oy1 = max(0, oy1)
                ox2 = min(w, ox2); oy2 = min(h, oy2)

                if ox2 <= ox1 or oy2 <= oy1:
                    continue

                boxes.append({
                    "bbox": [ox1, oy1, ox2, oy2],
                    "confidence": conf,
                    "label": label,
                    "class_id": cls_id,
                    "width": ox2 - ox1,
                    "height": oy2 - oy1,
                })
        return boxes

    def detect(self, image: np.ndarray) -> dict:
        start = time.time()
        self._load()
        orig_shape = image.shape[:2]

        if self._model is not None:
            import onnxruntime as ort
            input_tensor = self._preprocess(image)
            blob = np.transpose(input_tensor, (2, 0, 1)).astype(np.float32) / 255.0
            blob = np.expand_dims(blob, axis=0)

            input_name = self._model.get_inputs()[0].name
            outputs = self._model.run(None, {input_name: blob})[0]

            predictions = self._parse_yolo_output(outputs[0], orig_shape)
        elif self._model_pt is not None:
            input_tensor = self._preprocess(image)
            device = getattr(config, "GPU_DEVICE", 0) if getattr(config, "GPU_ENABLED", True) else "cpu"
            results = self._model_pt(
                input_tensor,
                conf=self._conf_threshold,
                iou=self._iou_threshold,
                classes=list(self._class_names.keys()),
                device=device,
                verbose=False,
            )
            predictions = self._postprocess(results[0], orig_shape)
        else:
            predictions = []

        best = max(predictions, key=lambda x: x["width"] * x["height"]) if predictions else None

        elapsed_ms = (time.time() - start) * 1000
        return {
            "vehicles": predictions,
            "best_vehicle": best,
            "vehicle_count": len(predictions),
            "processing_time_ms": elapsed_ms,
        }

    def _parse_yolo_output(self, output: np.ndarray, image_shape) -> list:
        h, w = image_shape[:2]
        scale = self._scale
        dx = self._dx
        dy = self._dy
        boxes = []

        output = output[output[:, 4] >= self._conf_threshold]
        if len(output) == 0:
            return boxes

        class_ids = np.argmax(output[:, 5:], axis=1)
        confs = output[:, 4] * np.max(output[:, 5:], axis=1)

        for i in range(len(output)):
            cls_id = int(class_ids[i])
            if cls_id not in self._class_names:
                continue

            cx, cy, bw, bh = output[i, :4]
            x1 = int((cx - bw / 2 - dx) / scale)
            y1 = int((cy - bh / 2 - dy) / scale)
            x2 = int((cx + bw / 2 - dx) / scale)
            y2 = int((cy + bh / 2 - dy) / scale)
            x1 = max(0, x1); y1 = max(0, y1)
            x2 = min(w, x2); y2 = min(h, y2)

            if x2 <= x1 or y2 <= y1:
                continue

            boxes.append({
                "bbox": [x1, y1, x2, y2],
                "confidence": float(confs[i]),
                "label": self._class_names[cls_id],
                "class_id": cls_id,
                "width": x2 - x1,
                "height": y2 - y1,
            })

        boxes.sort(key=lambda x: x["confidence"], reverse=True)
        keep = self._nms(boxes)
        return [boxes[i] for i in keep]

    def _nms(self, boxes: list) -> list:
        if not boxes:
            return []
        bboxes = np.array([b["bbox"] for b in boxes])
        scores = np.array([b["confidence"] for b in boxes])
        x1 = bboxes[:, 0]; y1 = bboxes[:, 1]
        x2 = bboxes[:, 2]; y2 = bboxes[:, 3]
        areas = (x2 - x1) * (y2 - y1)
        order = scores.argsort()[::-1]
        keep = []

        while len(order) > 0:
            i = order[0]
            keep.append(i)
            xx1 = np.maximum(x1[i], x1[order[1:]])
            yy1 = np.maximum(y1[i], y1[order[1:]])
            xx2 = np.minimum(x2[i], x2[order[1:]])
            yy2 = np.minimum(y2[i], y2[order[1:]])
            inter = np.maximum(0, xx2 - xx1) * np.maximum(0, yy2 - yy1)
            iou = inter / (areas[i] + areas[order[1:]] - inter + 1e-6)
            order = order[1:][iou < self._iou_threshold]

        return keep


def crop_vehicle(image: np.ndarray, bbox: list) -> np.ndarray:
    x1, y1, x2, y2 = map(int, bbox)
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(image.shape[1], x2), min(image.shape[0], y2)
    return image[y1:y2, x1:x2]
