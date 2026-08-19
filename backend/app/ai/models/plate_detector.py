import logging
import os
import time
import cv2
import numpy as np
from typing import List, Optional

from app.ai import config

logger = logging.getLogger(__name__)


class PlateDetector:
    def __init__(self):
        self._model = None
        self._model_pt = None
        self._input_size = config.PLATE_IMGSZ
        self._conf_threshold = config.PLATE_CONF_THRESHOLD
        self._iou_threshold = config.PLATE_IOU_THRESHOLD
        self._scale = 1.0
        self._dx = 0
        self._dy = 0

    def _load(self):
        if self._model is not None or self._model_pt is not None:
            return

        backend = getattr(config, "MODEL_BACKEND", "PYTORCH")
        if backend == "TENSORRT":
            raise NotImplementedError("TensorRT backend is not yet supported in Phase 12.1. Use ONNX or PYTORCH.")

        if backend == "ONNX" or (getattr(config, "ENABLE_ONNX", True) and os.path.exists(config.PLATE_DETECTION_MODEL_ONNX)):
            onnx_path = getattr(config, "PLATE_DETECTION_MODEL_ONNX", os.path.join(config.MODEL_DIR, "plate_detector.onnx"))
            if os.path.exists(onnx_path):
                try:
                    import onnxruntime as ort
                    providers = ["CUDAExecutionProvider", "CPUExecutionProvider"] if getattr(config, "GPU_ENABLED", True) else ["CPUExecutionProvider"]
                    avail_providers = [p for p in providers if p in ort.get_available_providers()]
                    if not avail_providers:
                        avail_providers = ort.get_available_providers()
                    session = ort.InferenceSession(onnx_path, providers=avail_providers)
                    out_shape = session.get_outputs()[0].shape
                    if out_shape and len(out_shape) >= 2 and out_shape[1] > 20:
                        logger.info("PLATE ONNX is 80-class COCO detector, skipping ONNX for plate model.")
                    else:
                        self._model = session
                        logger.info("Plate detector ONNX loaded")
                        return
                except Exception as e:
                    logger.warning(f"Plate ONNX load failed: {e}")

        if os.path.exists(config.PLATE_DETECTION_MODEL_PT) and os.path.abspath(config.PLATE_DETECTION_MODEL_PT) != os.path.abspath(config.VEHICLE_DETECTION_MODEL_PT):
            try:
                from ultralytics import YOLO
                self._model_pt = YOLO(config.PLATE_DETECTION_MODEL_PT)
                logger.info(f"Plate detector YOLO loaded: {config.PLATE_DETECTION_MODEL_PT}")
                return
            except Exception as e:
                logger.warning(f"Plate YOLO load failed: {e}")

        logger.info("No plate model found, will use OpenCV fallback")

    def detect(self, image: np.ndarray, vehicle_roi: Optional[np.ndarray] = None) -> dict:
        start = time.time()
        plates = []

        self._load()
        yolo_result = self._detect_yolo(image, vehicle_roi)

        if yolo_result and yolo_result.get("plates"):
            plates = yolo_result["plates"]
            logger.debug(f"YOLO plate detector found {len(plates)} plates")
        elif config.ENABLE_FALLBACK:
            fallback_result = self._detect_opencv(image, vehicle_roi)
            if fallback_result and fallback_result.get("plates"):
                plates = fallback_result["plates"]
                logger.debug(f"OpenCV fallback found {len(plates)} plates")

        plates.sort(key=lambda p: p["confidence"], reverse=True)
        best = plates[0] if plates else None

        elapsed_ms = (time.time() - start) * 1000
        return {
            "plate_found": best is not None,
            "best_plate": best,
            "plates": plates,
            "plate_count": len(plates),
            "processing_time_ms": elapsed_ms,
        }

    def _detect_yolo(self, image: np.ndarray, vehicle_roi: Optional[np.ndarray] = None) -> dict:
        if self._model is None and self._model_pt is None:
            return {"plates": [], "best_plate": None}

        target = vehicle_roi if vehicle_roi is not None else image
        target_h, target_w = target.shape[:2]

        if self._model is not None:
            import onnxruntime as ort
            input_tensor = self._preprocess(target)
            blob = np.transpose(input_tensor, (2, 0, 1)).astype(np.float32) / 255.0
            blob = np.expand_dims(blob, axis=0)
            input_name = self._model.get_inputs()[0].name
            outputs = self._model.run(None, {input_name: blob})[0]
            boxes = self._parse_yolo_output(outputs[0], (target_h, target_w))
        elif self._model_pt is not None:
            input_tensor = self._preprocess(target)
            import torch
            device = getattr(config, "GPU_DEVICE", 0) if (getattr(config, "GPU_ENABLED", True) and torch.cuda.is_available()) else "cpu"
            results = self._model_pt(
                input_tensor,
                conf=self._conf_threshold,
                iou=self._iou_threshold,
                device=device,
                verbose=False,
            )
            boxes = self._postprocess(results[0], (target_h, target_w))
        else:
            boxes = []

        if vehicle_roi is not None and hasattr(self, '_roi_offset'):
            for b in boxes:
                b["bbox"] = [
                    b["bbox"][0] + self._roi_offset[0],
                    b["bbox"][1] + self._roi_offset[1],
                    b["bbox"][2] + self._roi_offset[0],
                    b["bbox"][3] + self._roi_offset[1],
                ]

        return {"plates": boxes, "best_plate": boxes[0] if boxes else None}

    def _detect_opencv(self, image: np.ndarray, vehicle_roi: Optional[np.ndarray] = None) -> dict:
        plates = []
        roi = image
        offset_x, offset_y = 0, 0

        if vehicle_roi is not None:
            h, w = image.shape[:2]
            x1, y1, x2, y2 = vehicle_roi
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)
            roi = image[y1:y2, x1:x2]
            offset_x, offset_y = x1, y1
            if roi.size == 0:
                return {"plates": plates, "best_plate": None}

        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

        for method_name, processed in [
            ("bilateral+edge", self._edge_detect(gray)),
            ("otsu", self._otsu_threshold(gray)),
            ("adaptive", self._adaptive_threshold(gray)),
            ("sobel", self._sobel_detect(gray)),
        ]:
            candidates = self._find_plate_contours(processed, roi.shape)
            for c in candidates:
                c["bbox"] = [
                    c["bbox"][0] + offset_x, c["bbox"][1] + offset_y,
                    c["bbox"][2] + offset_x, c["bbox"][3] + offset_y,
                ]
                c["confidence"] *= 0.8
                c["detection_method"] = method_name
                plates.append(c)

        return {"plates": plates, "best_plate": plates[0] if plates else None}

    def _edge_detect(self, gray: np.ndarray) -> np.ndarray:
        bfilter = cv2.bilateralFilter(gray, 11, 17, 17)
        return cv2.Canny(bfilter, 30, 200)

    def _otsu_threshold(self, gray: np.ndarray) -> np.ndarray:
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return thresh

    def _adaptive_threshold(self, gray: np.ndarray) -> np.ndarray:
        return cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                     cv2.THRESH_BINARY, 11, 2)

    def _sobel_detect(self, gray: np.ndarray) -> np.ndarray:
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        mag = np.sqrt(sobelx ** 2 + sobely ** 2)
        mag = np.uint8(np.clip(mag / mag.max() * 255, 0, 255))
        _, thresh = cv2.threshold(mag, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return thresh

    def _find_plate_contours(self, edged: np.ndarray, roi_shape) -> list:
        plates = []
        contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:20]

        for contour in contours:
            area = cv2.contourArea(contour)
            if area < config.OPENCV_PLATE_MIN_AREA:
                continue

            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * peri, True)

            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / max(h, 1)

            if (config.OPENCV_PLATE_ASPECT_RATIO_MIN < aspect_ratio < config.OPENCV_PLATE_ASPECT_RATIO_MAX
                    and h > config.OPENCV_PLATE_MIN_HEIGHT
                    and w > config.OPENCV_PLATE_MIN_WIDTH):
                plates.append({
                    "bbox": [x, y, x + w, y + h],
                    "confidence": min(1.0, area / 10000),
                    "aspect_ratio": aspect_ratio,
                    "width": w,
                    "height": h,
                })

            elif len(approx) == 4:
                x, y, w, h = cv2.boundingRect(approx)
                aspect_ratio = w / max(h, 1)
                if (config.OPENCV_PLATE_ASPECT_RATIO_MIN < aspect_ratio < config.OPENCV_PLATE_ASPECT_RATIO_MAX
                        and h > config.OPENCV_PLATE_MIN_HEIGHT):
                    plates.append({
                        "bbox": [x, y, x + w, y + h],
                        "confidence": min(1.0, area / 8000),
                        "aspect_ratio": aspect_ratio,
                        "width": w,
                        "height": h,
                    })

        return plates

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

        if not hasattr(preds, "boxes"):
            return boxes

        for box in preds.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            conf = float(box.conf[0])
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
                "width": ox2 - ox1,
                "height": oy2 - oy1,
            })
        return boxes

    def _parse_yolo_output(self, output: np.ndarray, image_shape) -> list:
        h, w = image_shape[:2]
        scale = self._scale
        dx = self._dx
        dy = self._dy
        boxes = []

        output = output[output[:, 4] >= self._conf_threshold]
        if len(output) == 0:
            return boxes

        for i in range(len(output)):
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
                "confidence": float(output[i, 4]),
                "width": x2 - x1,
                "height": y2 - y1,
            })
        return boxes


def crop_plate(image: np.ndarray, plate_bbox: list) -> np.ndarray:
    x1, y1, x2, y2 = map(int, plate_bbox)
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(image.shape[1], x2), min(image.shape[0], y2)
    return image[y1:y2, x1:x2]
