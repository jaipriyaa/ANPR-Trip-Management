import cv2
import numpy as np
from typing import Optional


def correct_perspective(image: np.ndarray, plate_bbox: list, margin: int = 5) -> Optional[np.ndarray]:
    x1, y1, x2, y2 = plate_bbox
    x1 = max(0, x1 - margin)
    y1 = max(0, y1 - margin)
    x2 = min(image.shape[1], x2 + margin)
    y2 = min(image.shape[0], y2 + margin)

    plate_roi = image[y1:y2, x1:x2]
    if plate_roi.size == 0:
        return None

    h, w = plate_roi.shape[:2]
    if h > w * 1.5:
        plate_roi = cv2.rotate(plate_roi, cv2.ROTATE_90_CLOCKWISE)
        h, w = plate_roi.shape[:2]

    gray = cv2.cvtColor(plate_roi, cv2.COLOR_BGR2GRAY) if len(plate_roi.shape) == 3 else plate_roi

    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 100, minLineLength=w // 2, maxLineGap=10)

    if lines is not None and len(lines) > 2:
        angles = []
        for line in lines:
            line_data = line[0] if len(line.shape) > 1 else line
            if len(line_data) == 4:
                x1_l, y1_l, x2_l, y2_l = line_data
                angle = np.arctan2(float(y2_l - y1_l), float(x2_l - x1_l)) * 180.0 / np.pi
                angles.append(angle)

        angles = np.array(angles)
        median_angle = np.median(angles)

        if abs(median_angle) > 2:
            center = (w // 2, h // 2)
            rotation_matrix = cv2.getRotationMatrix2D(center, median_angle, 1.0)
            plate_roi = cv2.warpAffine(plate_roi, rotation_matrix, (w, h),
                                       flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    return plate_roi


def four_point_transform(image: np.ndarray, pts: np.ndarray) -> Optional[np.ndarray]:
    rect = _order_points(pts)
    (tl, tr, br, bl) = rect

    width_a = np.linalg.norm(br - bl)
    width_b = np.linalg.norm(tr - tl)
    max_width = max(int(width_a), int(width_b))

    height_a = np.linalg.norm(tr - br)
    height_b = np.linalg.norm(tl - bl)
    max_height = max(int(height_a), int(height_b))

    if max_width < 10 or max_height < 5:
        return None

    dst = np.array([
        [0, 0],
        [max_width - 1, 0],
        [max_width - 1, max_height - 1],
        [0, max_height - 1],
    ], dtype=np.float32)

    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (max_width, max_height))
    return warped


def _order_points(pts: np.ndarray) -> np.ndarray:
    rect = np.zeros((4, 2), dtype=np.float32)
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect


def deskew(image: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)

    coords = np.column_stack(np.where(binary > 0))
    if len(coords) < 10:
        return image

    angle = cv2.minAreaRect(coords[:, ::-1])[-1]
    if angle < -45:
        angle = 90 + angle
    angle = -angle

    if abs(angle) < 0.5:
        return image

    h, w = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h),
                             flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated
