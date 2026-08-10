import logging
import time
import numpy as np

logger = logging.getLogger(__name__)

_ocr_reader = None


def get_reader():
    global _ocr_reader
    if _ocr_reader is None:
        try:
            import easyocr
            _ocr_reader = easyocr.Reader(["en"], gpu=False, verbose=False)
            logger.info("EasyOCR reader initialized")
        except Exception as e:
            logger.error(f"Failed to initialize EasyOCR: {e}")
            raise
    return _ocr_reader


def perform_ocr(plate_crop: np.ndarray) -> dict:
    reader = get_reader()
    start = time.time()

    results = reader.readtext(plate_crop, paragraph=False, width_ths=0.1)

    best = None
    all_texts = []

    for bbox, text, conf in results:
        entry = {"text": text.strip().upper(), "confidence": float(conf), "bbox": bbox.tolist() if hasattr(bbox, "tolist") else bbox}
        all_texts.append(entry)
        if best is None or conf > best["confidence"]:
            best = entry

    elapsed_ms = (time.time() - start) * 1000

    return {
        "plate_text": best["text"] if best else "",
        "confidence": best["confidence"] if best else 0.0,
        "raw_text": best["text"] if best else "",
        "all_texts": all_texts,
        "processing_time_ms": elapsed_ms,
    }
