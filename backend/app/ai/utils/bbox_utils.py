import numpy as np
from typing import List, Tuple

def clip_bbox(bbox: List[int], image_shape: Tuple[int, int]) -> List[int]:
    """Clips bounding box coordinates [x1, y1, x2, y2] to within image dimensions (H, W)."""
    h, w = image_shape[:2]
    x1, y1, x2, y2 = map(int, bbox)
    x1 = max(0, min(x1, w - 1))
    y1 = max(0, min(y1, h - 1))
    x2 = max(x1 + 1, min(x2, w))
    y2 = max(y1 + 1, min(y2, h))
    return [x1, y1, x2, y2]

def pad_bbox(bbox: List[int], image_shape: Tuple[int, int], margin_pct: float = 0.05) -> List[int]:
    """Adds percentage-based padding margin around bounding box."""
    h, w = image_shape[:2]
    x1, y1, x2, y2 = bbox
    bw = x2 - x1
    bh = y2 - y1
    pad_w = int(bw * margin_pct)
    pad_h = int(bh * margin_pct)
    return clip_bbox([x1 - pad_w, y1 - pad_h, x2 + pad_w, y2 + pad_h], (h, w))

def scale_bbox(bbox: List[int], scale: float, dx: int, dy: int, orig_shape: Tuple[int, int]) -> List[int]:
    """Scales resized canvas bounding box coordinates back to original image dimensions."""
    x1, y1, x2, y2 = bbox
    ox1 = int((x1 - dx) / scale)
    oy1 = int((y1 - dy) / scale)
    ox2 = int((x2 - dx) / scale)
    oy2 = int((y2 - dy) / scale)
    return clip_bbox([ox1, oy1, ox2, oy2], orig_shape)

def compute_iou(boxA: List[int], boxB: List[int]) -> float:
    """Computes Intersection-over-Union (IoU) between two bounding boxes [x1, y1, x2, y2]."""
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    interArea = max(0, xB - xA) * max(0, yB - yA)
    if interArea == 0:
        return 0.0

    boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])
    iou = interArea / float(boxAArea + boxBArea - interArea + 1e-6)
    return iou

def _extract_box(b: dict) -> List[int]:
    return b.get("plate_bbox") or b.get("vehicle_bbox") or b.get("bbox") or [0, 0, 0, 0]

def non_max_suppression(boxes: List[dict], iou_threshold: float = 0.45) -> List[dict]:
    """Applies Non-Maximum Suppression to dict bounding boxes containing 'bbox', 'vehicle_bbox', or 'plate_bbox'."""
    if not boxes:
        return []

    sorted_boxes = sorted(boxes, key=lambda b: b.get("confidence", b.get("vehicle_confidence", 0.0)), reverse=True)
    keep = []

    while sorted_boxes:
        current = sorted_boxes.pop(0)
        keep.append(current)
        curr_box = _extract_box(current)
        sorted_boxes = [
            b for b in sorted_boxes
            if compute_iou(curr_box, _extract_box(b)) < iou_threshold
        ]

    return keep
