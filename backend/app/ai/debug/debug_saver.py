import os
import json
import logging
import time
import cv2
import numpy as np
from typing import Dict, List, Optional
from app.ai import config

logger = logging.getLogger(__name__)


class DebugSaver:
    """
    Debug Artifact Export Utility for Industrial ANPR System.
    Saves session artifacts, crops, annotated visualization, and JSON metadata.
    """

    def __init__(self, debug_dir: Optional[str] = None):
        self.debug_dir = debug_dir or getattr(config, "DEBUG_DIR", "debug")
        os.makedirs(self.debug_dir, exist_ok=True)

    def save_session(
        self,
        image: np.ndarray,
        annotated_img: np.ndarray,
        tracked_vehicles: List[Dict],
        payload: Dict,
        session_id: Optional[str] = None,
    ) -> Dict:
        """
        Saves session artifacts into debug directory if debug mode is enabled.
        """
        try:
            is_debug_enabled = os.getenv("DEBUG_MODE", "false").lower() in ("true", "1", "yes")
            if not is_debug_enabled:
                return payload

            sess_id = session_id or f"session_{int(time.time() * 1000)}"
            sess_dir = os.path.join(self.debug_dir, sess_id)
            os.makedirs(sess_dir, exist_ok=True)

            if isinstance(image, np.ndarray) and image.size > 0 and image.shape[0] > 10:
                cv2.imwrite(os.path.join(sess_dir, "raw_image.jpg"), image)

            if isinstance(annotated_img, np.ndarray) and annotated_img.size > 0 and annotated_img.shape[0] > 10:
                cv2.imwrite(os.path.join(sess_dir, "annotated_image.jpg"), annotated_img)

            clean_payload = json.dumps(payload, default=lambda o: str(o), indent=2)
            with open(os.path.join(sess_dir, "metadata.json"), "w", encoding="utf-8") as f:
                f.write(clean_payload)

            payload["debug_dir"] = sess_dir
        except Exception as e:
            logger.warning(f"DebugSaver error: {e}")

        return payload
