import os
import sys
import platform
import hashlib
import json

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

def verify_jetson():
    print("============================================================")
    print("      NVIDIA JETSON EDGE DEPLOYMENT VERIFICATION           ")
    print("============================================================")

    is_jetson = os.path.exists("/etc/nv_tegra_release")
    print(f"Is Jetson Hardware: {is_jetson}")
    if not is_jetson:
        print("JETSON HARDWARE: NOT AVAILABLE IN CURRENT ENVIRONMENT")

    import torch
    import cv2
    import onnx
    import onnxruntime as ort

    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version.split()[0]}")
    print(f"PyTorch: {torch.__version__} (CUDA: {torch.cuda.is_available()})")
    print(f"OpenCV: {cv2.__version__}")
    print(f"ONNXRuntime: {ort.__version__}")

    v_pt = os.path.abspath("models/vehicle_detector.pt")
    p_pt = os.path.abspath("models/license_plate_detector.pt")
    v_onnx = os.path.abspath("models/vehicle_detector.onnx")
    p_onnx = os.path.abspath("models/license_plate_detector.onnx")
    v_engine = os.path.abspath("models/tensorrt/vehicle_detector_fp16.engine")
    p_engine = os.path.abspath("models/tensorrt/license_plate_detector_fp16.engine")

    print("\nModel Integrity & Paths:")
    for name, path in [
        ("Vehicle PT", v_pt), ("Plate PT", p_pt),
        ("Vehicle ONNX", v_onnx), ("Plate ONNX", p_onnx),
        ("Vehicle Engine", v_engine), ("Plate Engine", p_engine)
    ]:
        exists = os.path.exists(path)
        size = os.path.getsize(path) if exists else 0
        print(f"  - {name}: {'EXISTS' if exists else 'MISSING'} (Size: {size} bytes)")

    print("============================================================")

if __name__ == "__main__":
    verify_jetson()
