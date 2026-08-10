"""
Enterprise Edge Hardware-Aware Backend Selector for Industrial ANPR Trip Management System.
Automatically selects and loads inference backends in priority order: TensorRT -> ONNX -> PyTorch.
"""

import os
import sys
import logging
from typing import Dict, Any, Tuple, Optional

from app.ai import config

logger = logging.getLogger(__name__)


def is_cuda_available() -> bool:
    """Checks if CUDA is available via PyTorch or ONNX Runtime."""
    try:
        import torch
        if torch.cuda.is_available():
            return True
    except ImportError:
        pass

    try:
        import onnxruntime as ort
        if "CUDAExecutionProvider" in ort.get_available_providers() or "TensorrtExecutionProvider" in ort.get_available_providers():
            return True
    except ImportError:
        pass

    return False


def is_tensorrt_available() -> bool:
    """Checks if TensorRT library or ONNX Runtime TensorRT Execution Provider is available."""
    try:
        import tensorrt
        return True
    except ImportError:
        pass

    try:
        import onnxruntime as ort
        if "TensorrtExecutionProvider" in ort.get_available_providers():
            return True
    except ImportError:
        pass

    return False


def is_onnx_available() -> bool:
    """Checks if ONNX Runtime is installed."""
    try:
        import onnxruntime
        return True
    except ImportError:
        return False


def is_pytorch_available() -> bool:
    """Checks if PyTorch & Ultralytics are installed."""
    try:
        import torch
        import ultralytics
        return True
    except ImportError:
        return False


def get_gpu_device_name() -> str:
    """Returns GPU device name if available."""
    try:
        import torch
        if torch.cuda.is_available():
            return torch.cuda.get_device_name(0)
    except Exception:
        pass
    return "N/A"


class BackendSelector:
    """
    Hardware-Aware Inference Backend Selector.
    Priority fallback order: TensorRT -> ONNX -> PyTorch.
    """

    def __init__(self, engine_path: str, onnx_path: str, pt_path: str, model_name: str = "Model"):
        self.engine_path = engine_path
        self.onnx_path = onnx_path
        self.pt_path = pt_path
        self.model_name = model_name

    def resolve_backend(self) -> str:
        requested = config.MODEL_BACKEND.upper()

        if requested == "TENSORRT":
            if os.path.exists(self.engine_path) and is_tensorrt_available():
                return "TENSORRT"
            logger.warning(f"[{self.model_name}] TensorRT requested, but engine file missing ({self.engine_path}) or TensorRT bindings not found. Falling back to ONNX.")
            requested = "ONNX"

        if requested == "ONNX":
            if os.path.exists(self.onnx_path) and is_onnx_available():
                return "ONNX"
            logger.warning(f"[{self.model_name}] ONNX requested, but file missing ({self.onnx_path}) or onnxruntime not found. Falling back to PyTorch.")
            requested = "PYTORCH"

        if requested == "PYTORCH":
            return "PYTORCH"

        # Default AUTO mode: TensorRT -> ONNX -> PyTorch
        if os.path.exists(self.engine_path) and is_tensorrt_available():
            logger.info(f"[{self.model_name}] AUTO backend selected: TENSORRT")
            return "TENSORRT"
        elif os.path.exists(self.onnx_path) and is_onnx_available():
            logger.info(f"[{self.model_name}] AUTO backend selected: ONNX")
            return "ONNX"
        else:
            logger.info(f"[{self.model_name}] AUTO backend selected: PYTORCH")
            return "PYTORCH"


def get_active_backend_info() -> Dict[str, Any]:
    """Provides system inference backend status for Health Check API."""
    cuda_ok = is_cuda_available()
    trt_ok = is_tensorrt_available()
    onnx_ok = is_onnx_available()
    pt_ok = is_pytorch_available()
    gpu_name = get_gpu_device_name()

    vehicle_engine_exists = os.path.exists(config.VEHICLE_DETECTION_MODEL_ENGINE)
    vehicle_onnx_exists = os.path.exists(config.VEHICLE_DETECTION_MODEL_ONNX)

    active_backend = config.MODEL_BACKEND.upper()
    if active_backend == "AUTO":
        if vehicle_engine_exists and trt_ok:
            active_backend = "TENSORRT"
        elif vehicle_onnx_exists and onnx_ok:
            active_backend = "ONNX"
        else:
            active_backend = "PYTORCH"

    return {
        "status": "healthy",
        "backend": active_backend,
        "inference_backend": f"{active_backend} ({'GPU: ' + gpu_name if (cuda_ok and gpu_name != 'N/A') else 'CPU'})",
        "tensorrt_available": trt_ok and vehicle_engine_exists,
        "onnx_available": onnx_ok and vehicle_onnx_exists,
        "pytorch_available": pt_ok,
        "cuda_available": cuda_ok,
        "gpu": gpu_name if cuda_ok else "N/A",
        "gpu_enabled": config.GPU_ENABLED,
        "model_version": config.AI_MODEL_VERSION,
        "vehicle_model": {
            "name": "YOLOv11n COCO",
            "classes": 80,
            "path": config.VEHICLE_DETECTION_MODEL_PT,
        },
        "plate_model": {
            "name": "Custom YOLOv11 License Plate Detector",
            "classes": 1,
            "class": "license_plate",
            "path": config.PLATE_DETECTION_MODEL_PT,
        },
    }

