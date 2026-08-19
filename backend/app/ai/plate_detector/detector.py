import logging
import os
import time
import cv2
import numpy as np
from typing import List, Dict, Optional, Tuple

from app.ai import config
from app.ai.utils.bbox_utils import scale_bbox, clip_bbox, non_max_suppression, pad_bbox, compute_iou

logger = logging.getLogger(__name__)


from app.ai.inference.backend_selector import BackendSelector


class PlateDetector:
    """
    Industrial Grade License Plate Detector.
    Supports TensorRT, ONNX Runtime, PyTorch YOLO, and multi-threshold OpenCV contour fallbacks.
    Detects front/rear, yellow/white, commercial, tilted, square, long, damaged, and dirty plates.
    """

    def __init__(self):
        self._model_trt = None
        self._model_onnx = None
        self._model_pt = None
        self._input_size = config.PLATE_IMGSZ
        self._conf_threshold = config.PLATE_CONF_THRESHOLD
        self._iou_threshold = config.PLATE_IOU_THRESHOLD
        self.selector = BackendSelector(
            engine_path=config.PLATE_DETECTION_MODEL_ENGINE,
            onnx_path=config.PLATE_DETECTION_MODEL_ONNX,
            pt_path=config.PLATE_DETECTION_MODEL_PT,
            model_name="Plate Detector",
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
                    config.PLATE_DETECTION_MODEL_ENGINE if os.path.exists(config.PLATE_DETECTION_MODEL_ENGINE) else config.PLATE_DETECTION_MODEL_ONNX,
                    providers=avail_providers,
                )
                logger.info(f"Plate detector TensorRT session loaded successfully with providers: {avail_providers}")
                return
            except Exception as e:
                logger.warning(f"Plate TensorRT load failed: {e}. Falling back to ONNX.")
                chosen_backend = "ONNX"

        # Prioritize PyTorch YOLO model if present
        if os.path.exists(config.PLATE_DETECTION_MODEL_PT) and os.path.abspath(config.PLATE_DETECTION_MODEL_PT) != os.path.abspath(config.VEHICLE_DETECTION_MODEL_PT):
            try:
                from ultralytics import YOLO
                self._model_pt = YOLO(config.PLATE_DETECTION_MODEL_PT)
                logger.info(f"ACTIVE PLATE MODEL (PyTorch YOLO): {config.PLATE_DETECTION_MODEL_PT}")
                return
            except Exception as e:
                logger.warning(f"Plate PyTorch YOLO load failed: {e}")

        if chosen_backend == "ONNX":
            if os.path.exists(config.PLATE_DETECTION_MODEL_ONNX):
                try:
                    import onnxruntime as ort
                    providers = ["CUDAExecutionProvider", "CPUExecutionProvider"] if config.GPU_ENABLED else ["CPUExecutionProvider"]
                    avail_providers = [p for p in providers if p in ort.get_available_providers()]
                    if not avail_providers:
                        avail_providers = ort.get_available_providers()
                    session = ort.InferenceSession(
                        config.PLATE_DETECTION_MODEL_ONNX,
                        providers=avail_providers,
                    )
                    out_shape = session.get_outputs()[0].shape
                    if out_shape and len(out_shape) >= 2 and out_shape[1] > 20:
                        logger.info("PLATE ONNX is 80-class COCO detector, skipping ONNX for plate model.")
                    else:
                        self._model_onnx = session
                        logger.info(f"ACTIVE PLATE MODEL (ONNX): {config.PLATE_DETECTION_MODEL_ONNX} with providers {avail_providers}")
                        return
                except Exception as e:
                    logger.warning(f"Plate ONNX load failed: {e}")

        logger.info("No deep learning plate model file found; using multi-method OpenCV plate detector.")

    def detect(self, image: np.ndarray, vehicle_bbox: Optional[List[int]] = None) -> dict:
        """
        Detects license plates in image. If vehicle_bbox is provided, crops vehicle ROI first.
        Returns dict containing 'plates', 'best_plate', 'plate_count', and 'processing_time_ms'.
        """
        start_time = time.time()
        self._load()

        if image is None or image.size == 0:
            return {
                "plates": [],
                "best_plate": None,
                "plate_count": 0,
                "processing_time_ms": 0.0,
            }

        orig_h, orig_w = image.shape[:2]
        roi = image
        offset_x, offset_y = 0, 0

        if vehicle_bbox is not None and len(vehicle_bbox) == 4:
            x1, y1, x2, y2 = clip_bbox(vehicle_bbox, (orig_h, orig_w))
            roi = image[y1:y2, x1:x2]
            offset_x, offset_y = x1, y1
            if roi.size == 0:
                roi = image
                offset_x, offset_y = 0, 0

        plates = []

        # 1. Primary Deep Learning Detection (YOLO / ONNX)
        dl_plates = self._detect_yolo(roi, offset_x, offset_y, (orig_h, orig_w))
        if dl_plates:
            plates.extend(dl_plates)

        # 2. OpenCV Fallback Detection if deep learning finds no plate or fallback is forced
        if not plates and config.ENABLE_FALLBACK:
            cv_plates = self._detect_opencv(roi, offset_x, offset_y, (orig_h, orig_w))
            plates.extend(cv_plates)

        # Filter duplicates via NMS
        plates = non_max_suppression(plates, iou_threshold=self._iou_threshold)
        plates.sort(key=lambda p: p["confidence"], reverse=True)

        best_plate = plates[0] if plates else None
        elapsed_ms = round((time.time() - start_time) * 1000, 2)

        return {
            "plates": plates,
            "best_plate": best_plate,
            "plate_count": len(plates),
            "processing_time_ms": elapsed_ms,
        }

    def _is_valid_candidate(self, full_box: List[int], roi_shape: Tuple[int, int], offset_x: int, offset_y: int) -> bool:
        pw = full_box[2] - full_box[0]
        ph = full_box[3] - full_box[1]
        if pw <= 0 or ph <= 0:
            return False
        
        p_area = float(pw * ph)
        roi_h, roi_w = roi_shape[:2]
        roi_area = float(roi_h * roi_w)
        rel_area = p_area / max(roi_area, 1.0)
        aspect_ratio = pw / float(max(ph, 1))

        local_y_center = ((full_box[1] + full_box[3]) / 2.0) - offset_y
        rel_y_center = local_y_center / float(max(roi_h, 1))

        # Reject oversized container body banners (>12% of vehicle crop area)
        if rel_area > 0.12 or rel_area < 0.001:
            return False

        # Reject extreme banner aspect ratios
        if aspect_ratio < 1.1 or aspect_ratio > 7.0:
            return False

        # Reject upper container roof/banner text (top 20% of vehicle crop)
        if rel_y_center < 0.20 and rel_area > 0.04:
            return False

        return True

    def _detect_yolo(self, roi: np.ndarray, offset_x: int, offset_y: int, full_shape: Tuple[int, int]) -> List[dict]:
        if self._model_onnx is None and self._model_pt is None:
            return []

        h, w = roi.shape[:2]
        target_w, target_h = self._input_size
        scale = min(target_w / max(w, 1), target_h / max(h, 1))
        nw, nh = int(w * scale), int(h * scale)
        resized = cv2.resize(roi, (nw, nh), interpolation=cv2.INTER_LINEAR)
        canvas = np.full((target_h, target_w, 3), 114, dtype=np.uint8)
        dx = (target_w - nw) // 2
        dy = (target_h - nh) // 2
        canvas[dy:dy + nh, dx:dx + nw] = resized

        plates = []

        if self._model_pt is not None:
            device = getattr(config, "GPU_DEVICE", 0) if getattr(config, "GPU_ENABLED", True) else "cpu"
            results = self._model_pt(canvas, conf=self._conf_threshold, iou=self._iou_threshold, device=device, verbose=False)
            if len(results) > 0 and hasattr(results[0], "boxes"):
                for box in results[0].boxes:
                    bx1, by1, bx2, by2 = map(int, box.xyxy[0].tolist())
                    conf = float(box.conf[0])
                    scaled = scale_bbox([bx1, by1, bx2, by2], scale, dx, dy, (h, w))
                    full_box = [
                        scaled[0] + offset_x,
                        scaled[1] + offset_y,
                        scaled[2] + offset_x,
                        scaled[3] + offset_y,
                    ]
                    full_box = clip_bbox(full_box, full_shape)

                    if not self._is_valid_candidate(full_box, roi.shape, offset_x, offset_y):
                        continue

                    plates.append({
                        "plate_bbox": full_box,
                        "confidence": round(conf, 4),
                        "width": full_box[2] - full_box[0],
                        "height": full_box[3] - full_box[1],
                        "method": "yolo",
                    })


        elif self._model_onnx is not None:
            blob = np.transpose(canvas, (2, 0, 1)).astype(np.float32) / 255.0
            blob = np.expand_dims(blob, axis=0)
            input_name = self._model_onnx.get_inputs()[0].name
            raw_output = self._model_onnx.run(None, {input_name: blob})[0]
            output = raw_output[0]
            if output.shape[0] < output.shape[1]:
                output = output.T

            for row in output:
                conf = float(row[4]) if len(row) > 4 else 0.0
                if conf < self._conf_threshold:
                    continue
                cx, cy, bw, bh = row[:4]
                bx1 = int(cx - bw / 2)
                by1 = int(cy - bh / 2)
                bx2 = int(cx + bw / 2)
                by2 = int(cy + bh / 2)

                scaled = scale_bbox([bx1, by1, bx2, by2], scale, dx, dy, (h, w))
                full_box = [
                    scaled[0] + offset_x,
                    scaled[1] + offset_y,
                    scaled[2] + offset_x,
                    scaled[3] + offset_y,
                ]
                full_box = clip_bbox(full_box, full_shape)

                plates.append({
                    "plate_bbox": full_box,
                    "confidence": round(conf, 4),
                    "width": full_box[2] - full_box[0],
                    "height": full_box[3] - full_box[1],
                    "method": "onnx",
                })

        return plates

    def _detect_opencv(self, roi: np.ndarray, offset_x: int, offset_y: int, full_shape: Tuple[int, int]) -> List[dict]:
        plates = []
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

        methods = [
            ("blackhat_morph", self._blackhat_morph(gray)),
            ("bilateral_edge", self._edge_detect(gray)),
            ("otsu_thresh", self._otsu_threshold(gray)),
            ("adaptive_thresh", self._adaptive_threshold(gray)),
            ("sobel_gradient", self._sobel_detect(gray)),
        ]

        roi_area = float(roi.shape[0] * roi.shape[1])
        max_allowed_area = 0.25 * roi_area

        for method_name, binary_img in methods:
            contours, _ = cv2.findContours(binary_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contours = sorted(contours, key=cv2.contourArea, reverse=True)[:15]

            for contour in contours:
                area = cv2.contourArea(contour)
                if area < config.OPENCV_PLATE_MIN_AREA or area > max_allowed_area:
                    continue

                rx, ry, rw, rh = cv2.boundingRect(contour)
                aspect_ratio = rw / float(max(rh, 1))

                if (config.OPENCV_PLATE_ASPECT_RATIO_MIN <= aspect_ratio <= config.OPENCV_PLATE_ASPECT_RATIO_MAX
                        and rh >= config.OPENCV_PLATE_MIN_HEIGHT
                        and rw >= config.OPENCV_PLATE_MIN_WIDTH):

                    full_box = clip_bbox([rx + offset_x, ry + offset_y, rx + rw + offset_x, ry + rh + offset_y], full_shape)
                    if not self._is_valid_candidate(full_box, roi.shape, offset_x, offset_y):
                        continue

                    aspect_score = max(0.0, 1.0 - abs(aspect_ratio - 3.8) / 4.0)
                    conf = min(0.90, max(0.40, (area / 12000.0) + 0.35)) * (0.6 + 0.4 * aspect_score)


                    plates.append({
                        "plate_bbox": full_box,
                        "confidence": round(conf, 4),
                        "width": full_box[2] - full_box[0],
                        "height": full_box[3] - full_box[1],
                        "aspect_ratio": round(aspect_ratio, 2),
                        "method": f"opencv_{method_name}",
                    })

        plates = non_max_suppression(plates, iou_threshold=0.3)
        plates.sort(key=lambda p: p["confidence"], reverse=True)
        return plates[:12]

    def _edge_detect(self, gray: np.ndarray) -> np.ndarray:
        bfilter = cv2.bilateralFilter(gray, 11, 17, 17)
        return cv2.Canny(bfilter, 30, 200)

    def _otsu_threshold(self, gray: np.ndarray) -> np.ndarray:
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return thresh

    def _adaptive_threshold(self, gray: np.ndarray) -> np.ndarray:
        return cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

    def _blackhat_morph(self, gray: np.ndarray) -> np.ndarray:
        rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (13, 5))
        blackhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, rect_kernel)
        sobelx = cv2.Sobel(blackhat, cv2.CV_32F, 1, 0, ksize=-1)
        sobelx = np.absolute(sobelx)
        min_val, max_val = np.min(sobelx), np.max(sobelx)
        sobelx = (255 * ((sobelx - min_val) / (max_val - min_val + 1e-6))).astype('uint8')
        morph = cv2.morphologyEx(sobelx, cv2.MORPH_CLOSE, rect_kernel)
        _, thresh = cv2.threshold(morph, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return thresh

    def _sobel_detect(self, gray: np.ndarray) -> np.ndarray:
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        mag = np.sqrt(sobelx ** 2 + sobely ** 2)
        mag = np.uint8(np.clip(mag / (mag.max() + 1e-6) * 255, 0, 255))
        _, thresh = cv2.threshold(mag, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return thresh

