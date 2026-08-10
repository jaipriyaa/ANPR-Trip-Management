import cv2
import numpy as np
from typing import List, Tuple
from app.ai import config
from app.ai.utils.bbox_utils import clip_bbox, pad_bbox


def crop_plate(image: np.ndarray, plate_bbox: List[int], pad_pct: float = config.CROP_MARGIN_PERCENT) -> np.ndarray:
    """Crops plate bounding box region with safety margins."""
    if image is None or image.size == 0 or len(plate_bbox) != 4:
        return np.array([])

    h, w = image.shape[:2]
    padded_box = pad_bbox(plate_bbox, (h, w), margin_pct=pad_pct)
    x1, y1, x2, y2 = padded_box
    cropped = image[y1:y2, x1:x2].copy()
    return cropped


def crop_plate_with_preprocessing(
    image: np.ndarray,
    plate_bbox: List[int],
    target_size: Tuple[int, int] = (config.PLATE_TARGET_WIDTH, config.PLATE_TARGET_HEIGHT)
) -> np.ndarray:
    """
    Crops plate bounding box, resizes to standard dimensions, and prepares contrast/brightness.
    (Note: Strictly performs no OCR).
    """
    raw_crop = crop_plate(image, plate_bbox)
    if raw_crop is None or raw_crop.size == 0:
        return np.array([])

    # Resize to target aspect ratio (e.g. 320x96)
    target_w, target_h = target_size
    resized = cv2.resize(raw_crop, (target_w, target_h), interpolation=cv2.INTER_CUBIC)
    return resized
