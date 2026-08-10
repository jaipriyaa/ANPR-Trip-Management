#!/usr/bin/env python3
"""
Enterprise Edge Hardware & Environment Diagnostic Suite for Industrial ANPR Trip Management System.
Checks CUDA, TensorRT, GPU device availability, ONNX Runtime, PyTorch, OpenCV, and EasyOCR.
Prints PASS or FAIL for each component and overall deployment readiness.
"""

import sys
import os
import platform
import logging
from pathlib import Path

# Add backend directory to sys.path
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")
logger = logging.getLogger("SystemCheck")


def check_cuda() -> bool:
    """Check CUDA Toolkit availability."""
    cuda_found = False
    try:
        import torch
        if torch.cuda.is_available():
            cuda_version = torch.version.cuda
            logger.info(f"✓ CUDA (via PyTorch): PASS (Version: {cuda_version})")
            cuda_found = True
    except Exception:
        pass

    if not cuda_found:
        try:
            import onnxruntime as ort
            providers = ort.get_available_providers()
            if "CUDAExecutionProvider" in providers or "TensorrtExecutionProvider" in providers:
                logger.info(f"✓ CUDA (via ONNX Runtime): PASS (Providers: {providers})")
                cuda_found = True
        except Exception:
            pass

    if not cuda_found:
        logger.warning("✗ CUDA: FAIL (CUDA GPU acceleration unavailable or CPU mode active)")
    return cuda_found


def check_gpu() -> bool:
    """Check GPU hardware device details."""
    try:
        import torch
        if torch.cuda.is_available():
            gpu_count = torch.cuda.device_count()
            gpu_name = torch.cuda.get_device_name(0)
            logger.info(f"✓ GPU Hardware: PASS ({gpu_count} GPU(s) detected: '{gpu_name}')")
            return True
    except Exception:
        pass
    logger.warning("✗ GPU Hardware: FAIL (No NVIDIA GPU device detected; running on CPU)")
    return False


def check_tensorrt() -> bool:
    """Check TensorRT bindings & execution provider."""
    trt_ok = False
    try:
        import tensorrt
        logger.info(f"✓ TensorRT Library: PASS (Version: {tensorrt.__version__})")
        trt_ok = True
    except ImportError:
        logger.info("  TensorRT Python bindings ('tensorrt') not found.")

    try:
        import onnxruntime as ort
        if "TensorrtExecutionProvider" in ort.get_available_providers():
            logger.info("✓ TensorRT Execution Provider (ONNX Runtime): PASS")
            trt_ok = True
    except Exception:
        pass

    if not trt_ok:
        logger.info("ℹ TensorRT: WARN/FAIL (TensorRT not installed or not built on Windows; required for Jetson hardware acceleration)")
    return trt_ok


def check_onnxruntime() -> bool:
    """Check ONNX Runtime installation."""
    try:
        import onnxruntime as ort
        logger.info(f"✓ ONNX Runtime: PASS (Version: {ort.__version__}, Providers: {ort.get_available_providers()})")
        return True
    except Exception as e:
        logger.error(f"✗ ONNX Runtime: FAIL ({e})")
        return False


def check_pytorch() -> bool:
    """Check PyTorch and Ultralytics installations."""
    try:
        import torch
        import ultralytics
        logger.info(f"✓ PyTorch: PASS (Version: {torch.__version__}, Ultralytics: {ultralytics.__version__})")
        return True
    except Exception as e:
        logger.error(f"✗ PyTorch: FAIL ({e})")
        return False


def check_opencv() -> bool:
    """Check OpenCV installation."""
    try:
        import cv2
        logger.info(f"✓ OpenCV: PASS (Version: {cv2.__version__})")
        return True
    except Exception as e:
        logger.error(f"✗ OpenCV: FAIL ({e})")
        return False


def check_easyocr() -> bool:
    """Check EasyOCR engine installation."""
    try:
        import easyocr
        logger.info(f"✓ EasyOCR: PASS (Version: {easyocr.__version__})")
        return True
    except Exception as e:
        logger.error(f"✗ EasyOCR: FAIL ({e})")
        return False


def main():
    print("=========================================================")
    print("INDUSTRIAL ANPR TRIP MANAGEMENT SYSTEM - SYSTEM DIAGNOSTICS")
    print(f"OS Platform: {platform.system()} {platform.release()} ({platform.machine()})")
    print(f"Python Version: {platform.python_version()}")
    print("=========================================================\n")

    results = {}
    results["PyTorch"] = check_pytorch()
    results["OpenCV"] = check_opencv()
    results["ONNX Runtime"] = check_onnxruntime()
    results["EasyOCR"] = check_easyocr()
    results["CUDA"] = check_cuda()
    results["GPU Hardware"] = check_gpu()
    results["TensorRT"] = check_tensorrt()

    print("\n=========================================================")
    print("SYSTEM DIAGNOSTICS SUMMARY")
    print("=========================================================")

    critical_passed = results["PyTorch"] and results["OpenCV"] and results["ONNX Runtime"] and results["EasyOCR"]

    for component, status in results.items():
        st_str = "PASS" if status else ("FAIL (Optional)" if component in ("CUDA", "GPU Hardware", "TensorRT") else "FAIL")
        print(f"  {component:<20}: {st_str}")

    print("=========================================================")
    if critical_passed:
        print("OVERALL STATUS: PASS - Core AI Pipeline & Inference Infrastructure Healthy!")
        sys.exit(0)
    else:
        print("OVERALL STATUS: FAIL - Critical dependencies missing.")
        sys.exit(1)


if __name__ == "__main__":
    main()
