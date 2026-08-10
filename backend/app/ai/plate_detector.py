import logging
import time
import cv2
import numpy as np

logger = logging.getLogger(__name__)


def detect_plate(image: np.ndarray, vehicle_bbox: list = None) -> dict:
    start = time.time()

    roi = image
    offset_x, offset_y = 0, 0

    if vehicle_bbox:
        x1, y1, x2, y2 = vehicle_bbox
        h, w = image.shape[:2]
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)
        roi = image[y1:y2, x1:x2]
        offset_x, offset_y = x1, y1

    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    bfilter = cv2.bilateralFilter(gray, 11, 17, 17)
    edged = cv2.Canny(bfilter, 30, 200)

    contours, _ = cv2.findContours(edged, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:15]

    best_plate = None
    plates = []

    for contour in contours:
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)

        if len(approx) == 4:
            x, y, w, h = cv2.boundingRect(approx)
            aspect_ratio = w / max(h, 1)

            if 2.0 < aspect_ratio < 6.0 and h > 15 and w > 60:
                plate_candidates = [
                    image[y + offset_y : y + offset_y + h, x + offset_x : x + offset_x + w]
                ]

                entry = {
                    "bbox": [x + offset_x, y + offset_y, x + offset_x + w, y + offset_y + h],
                    "confidence": min(1.0, cv2.contourArea(contour) / 5000),
                    "aspect_ratio": aspect_ratio,
                    "width": w,
                    "height": h,
                }
                plates.append(entry)

                if best_plate is None or (w * h) > (best_plate["width"] * best_plate["height"]):
                    best_plate = entry

    if not best_plate:
        h, w = image.shape[:2]
        roi_bottom = image[int(0.6 * h) : int(0.95 * h), int(0.05 * w) : int(0.95 * w)]
        gray2 = cv2.cvtColor(roi_bottom, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray2, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        contours2, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours2:
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / max(h, 1)
            if 2.0 < aspect_ratio < 6.0 and h > 15:
                bx = int(0.05 * w) + x + int(0.05 * w)
                by = int(0.6 * h) + y
                best_plate = {
                    "bbox": [bx, by, bx + w, by + h],
                    "confidence": 0.3,
                    "aspect_ratio": aspect_ratio,
                    "width": w,
                    "height": h,
                }
                plates.append(best_plate)
                break

    elapsed_ms = (time.time() - start) * 1000

    return {
        "plate_found": best_plate is not None,
        "best_plate": best_plate,
        "plates": plates,
        "plate_count": len(plates),
        "processing_time_ms": elapsed_ms,
    }


def correct_perspective(image: np.ndarray, plate_bbox: list) -> np.ndarray:
    x1, y1, x2, y2 = plate_bbox
    plate_roi = image[y1:y2, x1:x2]
    if plate_roi.size == 0:
        return None
    h, w = plate_roi.shape[:2]
    if h > w:
        plate_roi = cv2.rotate(plate_roi, cv2.ROTATE_90_CLOCKWISE)
    gray = cv2.cvtColor(plate_roi, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh


def crop_plate(image: np.ndarray, plate_bbox: list) -> np.ndarray:
    x1, y1, x2, y2 = plate_bbox
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(image.shape[1], x2), min(image.shape[0], y2)
    return image[y1:y2, x1:x2]
