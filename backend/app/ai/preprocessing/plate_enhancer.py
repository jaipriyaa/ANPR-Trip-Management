import logging
import cv2
import numpy as np
from typing import Optional

from app.ai import config

logger = logging.getLogger(__name__)


class PlateEnhancer:
    def __init__(self):
        self.target_width = config.PLATE_WIDTH
        self.target_height = config.PLATE_HEIGHT
        self.clahe = cv2.createCLAHE(
            clipLimit=config.CLAHE_CLIP_LIMIT,
            tileGridSize=config.CLAHE_GRID_SIZE,
        )
        self.sharpen_kernel = np.array([
            [0, -1, 0],
            [-1, 5 + config.SHARPEN_STRENGTH, -1],
            [0, -1, 0],
        ])
        self.denoise_strength = config.DENOISE_STRENGTH

    def enhance(self, plate_crop: np.ndarray) -> np.ndarray:
        if plate_crop is None or plate_crop.size == 0:
            return plate_crop

        result = self._resize(plate_crop)
        result = self._denoise(result)
        result = self._grayscale(result)
        result = self._clahe(result)
        result = self._sharpen(result)
        result = self._normalize(result)
        return result

    def enhance_color(self, plate_crop: np.ndarray) -> np.ndarray:
        if plate_crop is None or plate_crop.size == 0:
            return plate_crop

        result = self._resize(plate_crop)
        result = self._denoise(result)
        lab = cv2.cvtColor(result, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        l = self.clahe.apply(l)
        lab = cv2.merge([l, a, b])
        result = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        result = self._sharpen(result)
        result = self._normalize(result)
        return result

    def _resize(self, image: np.ndarray) -> np.ndarray:
        h, w = image.shape[:2]
        if w < 10 or h < 5:
            return image
        aspect = w / max(h, 1)
        target_h = self.target_height
        target_w = int(target_h * aspect)
        target_w = min(target_w, self.target_width * 2)
        target_w = max(target_w, self.target_width // 2)
        return cv2.resize(image, (target_w, target_h), interpolation=cv2.INTER_CUBIC)

    def _denoise(self, image: np.ndarray) -> np.ndarray:
        return cv2.fastNlMeansDenoising(
            image if len(image.shape) == 2 else image,
            None,
            self.denoise_strength,
            7,
            21,
        )

    def _grayscale(self, image: np.ndarray) -> np.ndarray:
        if len(image.shape) == 3:
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return image

    def _clahe(self, gray: np.ndarray) -> np.ndarray:
        return self.clahe.apply(gray)

    def _sharpen(self, image: np.ndarray) -> np.ndarray:
        if len(image.shape) == 2:
            return cv2.filter2D(image, -1, self.sharpen_kernel)
        return cv2.filter2D(image, -1, self.sharpen_kernel)

    def _normalize(self, image: np.ndarray) -> np.ndarray:
        return cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX)
