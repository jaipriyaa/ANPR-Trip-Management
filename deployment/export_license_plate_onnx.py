import os
import sys
import torch
from ultralytics import YOLO

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PT = os.path.join(PROJECT_ROOT, "models", "license_plate_detector.pt")
MODEL_ONNX = os.path.join(PROJECT_ROOT, "models", "license_plate_detector.onnx")

print("=" * 80)
print("     STEP 14: EXPORT & VERIFY LICENSE PLATE DETECTOR ONNX MODEL     ")
print("=" * 80)

if not os.path.exists(MODEL_PT):
    print(f"[ERROR] Trained PyTorch model not found: {MODEL_PT}")
    sys.exit(1)

model = YOLO(MODEL_PT)
print(f"Loaded PyTorch Model: {MODEL_PT}")
print(f"Class Count : {len(model.names)}")
print(f"Class Names : {model.names}")

# Export to ONNX
print("\nExporting to ONNX format...")
exported_path = model.export(format="onnx", imgsz=640, simplify=True)

if os.path.exists(exported_path) and exported_path != MODEL_ONNX:
    import shutil
    shutil.copy(exported_path, MODEL_ONNX)

print(f"[OK] Exported ONNX Model saved to: {MODEL_ONNX}")

# Verify ONNX tensor input/output shapes using ONNX Runtime
try:
    import onnxruntime as ort
    session = ort.InferenceSession(MODEL_ONNX, providers=["CPUExecutionProvider"])
    inputs = session.get_inputs()
    outputs = session.get_outputs()

    print("\n[VERIFICATION] ONNX Model Tensor Metadata:")
    print(f"  Input Name : {inputs[0].name}, Shape: {inputs[0].shape}, Type: {inputs[0].type}")
    print(f"  Output Name: {outputs[0].name}, Shape: {outputs[0].shape}, Type: {outputs[0].type}")

    # Output shape for 1-class YOLOv11: [1, 5, 8400] (4 bbox coordinates + 1 class probability)
    out_shape = outputs[0].shape
    print(f"  Channel Dimension (num_classes + 4): {out_shape[1]}")

    if out_shape[1] == 5:
        print("[SUCCESS] Verified single-class license plate ONNX model output shape [1, 5, 8400]!")
    else:
        print(f"[WARNING] Expected 5 channels (1 class + 4 bbox), got {out_shape[1]}")

except Exception as e:
    print(f"[WARNING] ONNX runtime inspection error: {e}")

print("=" * 80)
