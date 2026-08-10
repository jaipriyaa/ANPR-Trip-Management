import os
import sys
from ultralytics import YOLO

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PT = os.path.join(PROJECT_ROOT, "models", "license_plate_detector.pt")
MODEL_ONNX = os.path.join(PROJECT_ROOT, "models", "license_plate_detector.onnx")

print("=" * 80)
print("     SINGLE-CLASS LICENSE PLATE ONNX EXPORTER & VERIFIER (PHASE 26-27)     ")
print("=" * 80)

if not os.path.exists(MODEL_PT):
    print(f"[ERROR] Fine-tuned model not found at {MODEL_PT}")
    sys.exit(1)

# Export PyTorch model to ONNX
print(f"Exporting PyTorch model {MODEL_PT} -> ONNX...")
model = YOLO(MODEL_PT)
exported_path = model.export(format="onnx", imgsz=640, dynamic=False)

if os.path.exists(exported_path):
    if exported_path != MODEL_ONNX:
        import shutil
        shutil.copy(exported_path, MODEL_ONNX)
    print(f"ONNX Export successful -> {MODEL_ONNX}")

# Verify ONNX structure and tensor shapes
import onnxruntime as ort
session = ort.InferenceSession(MODEL_ONNX, providers=["CPUExecutionProvider"])
inputs = session.get_inputs()
outputs = session.get_outputs()

inp_shape = inputs[0].shape
out_shape = outputs[0].shape

print("\n--- ONNX TENSOR SHAPE VERIFICATION ---")
print(f"Input Shape  : {inp_shape}")
print(f"Output Shape : {out_shape}")

num_channels = out_shape[1]
num_classes = num_channels - 4

print(f"Total Output Channels : {num_channels} (4 bbox coords + {num_classes} class probabilities)")
print(f"Verified Class Count  : {num_classes}")

if num_classes == 1:
    print("\n[VERIFIED PASS] ONNX Plate Detector has exactly 1 class (license_plate)!")
    print("                The old fake 80-class COCO ONNX model has been COMPLETELY REPLACED.")
else:
    print(f"\n[FAIL] Unexpected class count {num_classes} (Expected 1)")

print("=" * 80)
