import logging
import time
import re
import cv2
import numpy as np
from typing import List, Optional

from app.ai import config

logger = logging.getLogger(__name__)


class OCREngine:
    def __init__(self):
        self._easyocr = None
        self._paddleocr = None
        self.char_whitelist = set(config.OCR_CHAR_WHITELIST)
        self.conf_threshold = config.OCR_CONFIDENCE_THRESHOLD
        self._gpu = config.OCR_GPU

    def _init_easyocr(self):
        if self._easyocr is not None:
            return
        try:
            import easyocr
            self._easyocr = easyocr.Reader(["en"], gpu=self._gpu, verbose=False)
            logger.info(f"EasyOCR initialized (GPU={self._gpu})")
        except Exception as e:
            logger.error(f"Failed to init EasyOCR: {e}")
            raise

    def _filter_text(self, text: str) -> str:
        return "".join(c for c in text.upper() if c in self.char_whitelist)

    def read(self, image: np.ndarray) -> dict:
        self._init_easyocr()
        start = time.time()
        results = []

        image_rgb = self._prepare_image(image)

        raw_results = self._easyocr.readtext(
            image_rgb,
            paragraph=False,
            width_ths=0.1,
            decoder="greedy",
            beamWidth=5,
            batch_size=config.OCR_BATCH_SIZE,
        )

        for bbox, text, conf in raw_results:
            if conf < self.conf_threshold:
                continue
            filtered = self._filter_text(text)
            if not filtered:
                continue

            entry = {
                "text": filtered,
                "raw_text": text.strip().upper(),
                "confidence": float(conf),
                "bbox": bbox.tolist() if hasattr(bbox, "tolist") else bbox,
            }
            results.append(entry)

        if not results:
            elapsed_ms = (time.time() - start) * 1000
            return {
                "plate_text": "",
                "confidence": 0.0,
                "raw_text": "",
                "all_texts": [],
                "char_scores": [],
                "processing_time_ms": elapsed_ms,
            }

        # Order detected bounding boxes: top-to-bottom, left-to-right
        def get_bbox_sort_key(r):
            bb = r.get("bbox")
            if bb and isinstance(bb, (list, tuple)) and len(bb) > 0:
                pt = bb[0]
                if isinstance(pt, (list, tuple)) and len(pt) >= 2:
                    return (pt[1] // 20, pt[0])
            return (0, 0)

        sorted_results = sorted(results, key=get_bbox_sort_key)
        combined_text = "".join(r["text"] for r in sorted_results)
        combined_raw = " ".join(r["raw_text"] for r in sorted_results)
        avg_conf = float(sum(r["confidence"] for r in sorted_results) / len(sorted_results))

        char_scores = self._get_char_scores(image_rgb, combined_text)
        elapsed_ms = (time.time() - start) * 1000

        return {
            "plate_text": combined_text,
            "confidence": round(avg_conf, 4),
            "raw_text": combined_raw,
            "all_texts": results,
            "char_scores": char_scores,
            "processing_time_ms": elapsed_ms,
        }

    def read_ensemble(self, image: np.ndarray, image_enhanced: Optional[np.ndarray] = None) -> dict:
        if getattr(config, "PLATE_OCR_MODE", "ROBUST") == "ROBUST":
            return self.read_robust(image, image_enhanced)

        result1 = self.read(image)

        if image_enhanced is None or getattr(image_enhanced, "size", 0) == 0:
            try:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
                clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
                enhanced_gray = clahe.apply(gray)
                image_enhanced = cv2.cvtColor(enhanced_gray, cv2.COLOR_GRAY2BGR)
            except Exception:
                image_enhanced = None

        if image_enhanced is not None and getattr(image_enhanced, "size", 0) > 0:
            result2 = self.read(image_enhanced)
        else:
            result2 = {"plate_text": "", "confidence": 0.0, "raw_text": "", "all_texts": [], "char_scores": [], "processing_time_ms": 0.0}

        if not result1["plate_text"] and not result2["plate_text"]:
            return result1
        if not result1["plate_text"]:
            return result2
        if not result2["plate_text"]:
            return result1

        # Prefer longer or higher confidence result
        if len(result2["plate_text"]) > len(result1["plate_text"]) or (len(result2["plate_text"]) == len(result1["plate_text"]) and result2["confidence"] > result1["confidence"]):
            winner = result2
        else:
            winner = result1

        return {
            "plate_text": winner["plate_text"],
            "confidence": winner["confidence"],
            "raw_text": winner["raw_text"],
            "all_texts": result1["all_texts"] + result2["all_texts"],
            "char_scores": winner.get("char_scores", []),
            "processing_time_ms": result1["processing_time_ms"] + result2["processing_time_ms"],
        }

    def read_robust(self, image: np.ndarray, image_enhanced: Optional[np.ndarray] = None, validator=None) -> dict:
        self._init_easyocr()
        if image is None or getattr(image, "size", 0) == 0:
            return self.read(image)

        if validator is None:
            from app.ai.postprocessing.plate_validator import IndianPlateValidator
            validator = IndianPlateValidator()

        # Fast high-yield variants evaluated lazily
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image.copy()
        h, w = gray.shape[:2]

        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))

        variant_generators = [
            ("original", lambda: self._prepare_image(image)),
            ("enhanced", lambda: self._prepare_image(image_enhanced) if (image_enhanced is not None and getattr(image_enhanced, "size", 0) > 0) else None),
            ("clahe", lambda: cv2.cvtColor(clahe.apply(gray), cv2.COLOR_GRAY2BGR)),
            ("upscale_2x", lambda: cv2.resize(image, (max(320, w * 2), max(96, h * 2)), interpolation=cv2.INTER_CUBIC)),
            ("contrast", lambda: cv2.cvtColor(cv2.convertScaleAbs(gray, alpha=1.5, beta=10), cv2.COLOR_GRAY2BGR)),
            ("grayscale", lambda: cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)),
            ("sharpened", lambda: cv2.cvtColor(cv2.filter2D(gray, -1, np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])), cv2.COLOR_GRAY2BGR)),
            ("otsu", lambda: cv2.cvtColor(cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1], cv2.COLOR_GRAY2BGR)),
            ("upscale_3x", lambda: cv2.resize(image, (max(320, w * 3), max(96, h * 3)), interpolation=cv2.INTER_CUBIC)),
            ("denoised", lambda: cv2.cvtColor(cv2.fastNlMeansDenoising(gray, None, h=10, templateWindowSize=7, searchWindowSize=21), cv2.COLOR_GRAY2BGR)),
        ]

        candidates = []
        for name, gen_fn in variant_generators[:3]:
            var_img = gen_fn()
            if var_img is None:
                continue

            ocr_res = self.read(var_img)
            plate_txt = ocr_res.get("plate_text", "")
            raw_txt = ocr_res.get("raw_text", "")
            conf = ocr_res.get("confidence", 0.0)

            if not plate_txt:
                continue

            val_res = validator.correct_with_confidence(plate_txt, conf)
            is_valid = val_res.get("is_valid", False)
            norm_txt = val_res.get("plate_text", plate_txt)

            cand = {
                "variant": name,
                "plate_text": norm_txt,
                "raw_text": raw_txt,
                "confidence": conf,
                "is_valid": is_valid,
                "ocr_res": ocr_res,
            }
            candidates.append(cand)

            # Early exit: If valid Indian plate is recognized, stop evaluating further variants immediately
            if is_valid:
                break

        if not candidates:
            return self.read(image)

        # Select highest-scoring candidate: prefer valid Indian plates first
        valid_cands = [c for c in candidates if c["is_valid"]]
        if valid_cands:
            best = max(valid_cands, key=lambda c: (c["confidence"], len(c["plate_text"])))
        else:
            best = max(candidates, key=lambda c: (c["confidence"], len(c["plate_text"])))

        return {
            "plate_text": best["plate_text"],
            "confidence": best["confidence"],
            "raw_text": best["raw_text"],
            "variant": best["variant"],
            "all_texts": best["ocr_res"].get("all_texts", []),
            "char_scores": best["ocr_res"].get("char_scores", []),
            "processing_time_ms": best["ocr_res"].get("processing_time_ms", 0.0),
        }

    def _prepare_image(self, image: np.ndarray) -> np.ndarray:
        if image is None or getattr(image, "size", 0) == 0:
            return np.zeros((96, 320, 3), dtype=np.uint8)

        if len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

        h, w = image.shape[:2]
        # Upscale low-res plate images so characters are large enough for EasyOCR
        min_w, min_h = 320, 96
        if w < min_w or h < min_h:
            scale = max(min_w / max(w, 1), min_h / max(h, 1))
            nw, nh = max(min_w, int(w * scale)), max(min_h, int(h * scale))
            image = cv2.resize(image, (nw, nh), interpolation=cv2.INTER_CUBIC)

        return image

    def _get_char_scores(self, image: np.ndarray, plate_text: str) -> list:
        char_scores = []
        try:
            h, w = image.shape[:2]
            char_w = w / max(len(plate_text), 1)
            for i, char in enumerate(plate_text):
                x1 = max(0, int(i * char_w))
                x2 = min(w, int((i + 1) * char_w))
                y1, y2 = 0, h
                char_crop = image[y1:y2, x1:x2]
                if char_crop.size > 0:
                    char_scores.append({
                        "char": char,
                        "position": i,
                        "confidence": 1.0,
                    })
        except Exception:
            pass
        return char_scores

    @staticmethod
    def text_match(r: dict) -> bool:
        return bool(r.get("plate_text"))
