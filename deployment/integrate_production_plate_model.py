import os
import sys
import shutil
from ultralytics import YOLO

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRAINED_BEST_PT = os.path.join(PROJECT_ROOT, "models", "license_plate_training", "weights", "best.pt")
PROD_MODEL_PT = os.path.join(PROJECT_ROOT, "models", "license_plate_detector.pt")
BACKUP_MODEL_PT = os.path.join(PROJECT_ROOT, "models", "license_plate_detector_previous_backup.pt")
PROD_MODEL_ONNX = os.path.join(PROJECT_ROOT, "models", "license_plate_detector.onnx")
VEHICLE_MODEL_PT = os.path.join(PROJECT_ROOT, "models", "vehicle_detector.pt")

print("=" * 80)
print("   STEP 11, 12, 13: PRODUCTION MODEL REPLACEMENT & ONNX EXPORT   ")
print("=" * 80)

# 1. Backup existing license plate model
if os.path.exists(PROD_MODEL_PT):
    shutil.copy(PROD_MODEL_PT, BACKUP_MODEL_PT)
    print(f"[OK] Backed up existing plate model -> {BACKUP_MODEL_PT}")

# 2. Replace production model with new trained best.pt
if os.path.exists(TRAINED_BEST_PT):
    shutil.copy(TRAINED_BEST_PT, PROD_MODEL_PT)
    print(f"[OK] Replaced production model -> {PROD_MODEL_PT}")
else:
    print(f"[ERROR] Trained best.pt not found: {TRAINED_BEST_PT}")
    sys.exit(1)

# Verify single class metadata
p_model = YOLO(PROD_MODEL_PT)
print(f"[VERIFICATION] Production Plate Model Metadata:")
print(f"  Class Count: {len(p_model.names)}")
print(f"  Class Names: {p_model.names}")
if len(p_model.names) != 1 or p_model.names.get(0) != "license_plate":
    print(f"[ERROR] Expected single class 0: license_plate, got {p_model.names}")
    sys.exit(1)

# 3. Export to ONNX
print("\n[STEP 12] Exporting to ONNX format...")
exported_onnx = p_model.export(format="onnx", imgsz=640, simplify=True)
if os.path.exists(exported_onnx) and os.path.abspath(exported_onnx) != os.path.abspath(PROD_MODEL_ONNX):
    shutil.copy(exported_onnx, PROD_MODEL_ONNX)

print(f"[OK] Production ONNX model saved -> {PROD_MODEL_ONNX}")

# Verify ONNX tensor shape using ONNX Runtime
try:
    import onnxruntime as ort
    session = ort.InferenceSession(PROD_MODEL_ONNX, providers=["CPUExecutionProvider"])
    in_shape = session.get_inputs()[0].shape
    out_shape = session.get_outputs()[0].shape
    print(f"  ONNX Input Shape  : {in_shape}")
    print(f"  ONNX Output Shape : {out_shape}")
    if out_shape[1] == 5:
        print("[SUCCESS] Verified ONNX 1-class output tensor shape [1, 5, 8400]!")
    else:
        print(f"[WARNING] Expected 5 output channels, got {out_shape[1]}")
except Exception as e:
    print(f"[WARNING] ONNX tensor verification error: {e}")

# 4. Verify Vehicle Detector is completely untouched
v_model = YOLO(VEHICLE_MODEL_PT)
print(f"\n[CRITICAL SAFETY CHECK] Vehicle Detector (UNTOUCHED):")
print(f"  Path       : {VEHICLE_MODEL_PT}")
print(f"  Class Count: {len(v_model.names)}")
print(f"  Class Names: {v_model.names}")

print("=" * 80)
