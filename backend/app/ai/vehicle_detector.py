import logging
import time
import os
import cv2
import numpy as np

logger = logging.getLogger(__name__)

_model = None

VEHICLE_CLASSES = {0: "car", 1: "motorcycle", 2: "bus", 3: "truck"}
COCO_VEHICLE_CLASSES = VEHICLE_CLASSES


def get_model():
    global _model
    if _model is None:
        try:
            from ultralytics import YOLO
            from app.ai import config
            model_path = config.VEHICLE_DETECTION_MODEL_PT
            if not os.path.exists(model_path):
                model_path = "models/vehicle_detector.pt"
            if not os.path.exists(model_path):
                model_path = "backend/yolo11n.pt"
            _model = YOLO(model_path)
            logger.info(f"Vehicle detector model loaded from {model_path}")
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {e}")
            raise
    return _model


def detect_vehicle(image: np.ndarray, conf_threshold: float = 0.5) -> dict:
    model = get_model()
    start = time.time()

    from app.ai import config
    device = getattr(config, "GPU_DEVICE", 0) if getattr(config, "GPU_ENABLED", True) else "cpu"
    results = model(image, conf=conf_threshold, classes=list(COCO_VEHICLE_CLASSES.keys()), device=device, verbose=False)

    vehicles = []
    best = None

    for r in results:
        for box in r.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            conf = float(box.conf[0])
            cls_id = int(box.cls[0])
            label = COCO_VEHICLE_CLASSES.get(cls_id, "unknown")
            w, h = x2 - x1, y2 - y1
            entry = {
                "bbox": [x1, y1, x2, y2],
                "confidence": conf,
                "label": label,
                "width": w,
                "height": h,
            }
            vehicles.append(entry)
            if best is None or (w * h) > (best["width"] * best["height"]):
                best = entry

    elapsed_ms = (time.time() - start) * 1000

    return {
        "vehicles": vehicles,
        "best_vehicle": best,
        "vehicle_count": len(vehicles),
        "processing_time_ms": elapsed_ms,
    }


def crop_vehicle(image: np.ndarray, bbox: list) -> np.ndarray:
    x1, y1, x2, y2 = bbox
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(image.shape[1], x2), min(image.shape[0], y2)
    return image[y1:y2, x1:x2]
