import cv2
import numpy as np
from typing import List, Dict, Tuple
from app.ai import config


def get_class_color(vehicle_type: str) -> Tuple[int, int, int]:
    """Returns color tuple (BGR) corresponding to vehicle class."""
    return config.VEHICLE_CLASS_COLORS.get(vehicle_type, config.VEHICLE_CLASS_COLORS["Vehicle"])


def draw_badge(
    img: np.ndarray,
    text: str,
    pt: Tuple[int, int],
    bg_color: Tuple[int, int, int],
    text_color: Tuple[int, int, int] = (255, 255, 255),
    font_scale: float = 0.5,
    thickness: int = 1,
):
    """Draws a clean filled text badge on the image."""
    font = cv2.FONT_HERSHEY_SIMPLEX
    (tw, th), baseline = cv2.getTextSize(text, font, font_scale, thickness)
    x, y = pt
    x = max(0, min(x, img.shape[1] - tw - 4))
    y = max(th + 4, min(y, img.shape[0] - 4))

    # Background rectangle
    cv2.rectangle(
        img,
        (x, y - th - baseline - 4),
        (x + tw + 6, y + baseline),
        bg_color,
        -1,
    )
    # Text
    cv2.putText(
        img,
        text,
        (x + 3, y - baseline - 1),
        font,
        font_scale,
        text_color,
        thickness,
        cv2.LINE_AA,
    )


def annotate_image(
    image: np.ndarray,
    vehicles: List[dict],
    plates: List[dict] = None
) -> np.ndarray:
    """
    Renders high-quality visualization overlays with distinct colors per vehicle class,
    labels, tracking IDs, confidence scores, and plate bounding boxes.
    """
    if image is None or image.size == 0:
        return image

    annotated = image.copy()

    # 1. Draw Vehicles
    for veh in vehicles:
        bbox = veh.get("vehicle_bbox")
        if not bbox or len(bbox) != 4:
            continue

        v_type = veh.get("vehicle_type", "Vehicle")
        v_conf = veh.get("vehicle_confidence", 0.0)
        track_id = veh.get("tracking_id", "")
        color = get_class_color(v_type)

        x1, y1, x2, y2 = map(int, bbox)

        # Draw vehicle bounding box with 2px thickness
        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)

        # Build label text
        if track_id:
            label_text = f"[{track_id}] {v_type} {int(v_conf * 100)}%"
        else:
            label_text = f"{v_type} {int(v_conf * 100)}%"

        draw_badge(annotated, label_text, (x1, y1 - 2), bg_color=color, text_color=(0, 0, 0) if sum(color) > 400 else (255, 255, 255))

    # 2. Draw License Plates
    if plates:
        for plate in plates:
            p_bbox = plate.get("plate_bbox")
            if not p_bbox or len(p_bbox) != 4:
                continue

            p_conf = plate.get("confidence", 0.0)
            px1, py1, px2, py2 = map(int, p_bbox)
            p_color = config.PLATE_COLOR

            # Draw license plate bounding box with bright cyan/yellow
            cv2.rectangle(annotated, (px1, py1), (px2, py2), p_color, 2)

            # Label text
            plate_label = f"PLATE {int(p_conf * 100)}%"
            draw_badge(annotated, plate_label, (px1, py1 - 2), bg_color=p_color, text_color=(0, 0, 0))

    return annotated
