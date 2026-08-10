import os
import sys
import shutil
import time
from ultralytics import YOLO

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_YAML = os.path.join(PROJECT_ROOT, "datasets", "license_plate_detection", "data.yaml")
BASE_MODEL_PT = os.path.join(PROJECT_ROOT, "backend", "yolo11n.pt")
TRAIN_OUT_DIR = os.path.join(PROJECT_ROOT, "runs", "detect", "models", "license_plate_training")
CANONICAL_MODEL_PT = os.path.join(PROJECT_ROOT, "models", "license_plate_detector.pt")

print("=" * 80)
print("     STEP 5 & 6: 10-EPOCH YOLOv11 LICENSE PLATE DETECTOR TRAINING     ")
print("=" * 80)

if not os.path.exists(DATASET_YAML):
    print(f"[ERROR] Dataset yaml not found: {DATASET_YAML}")
    sys.exit(1)

base_pt = BASE_MODEL_PT if os.path.exists(BASE_MODEL_PT) else "yolo11n.pt"
print(f"Base Checkpoint : {base_pt}")
print(f"Dataset YAML    : {DATASET_YAML}")
print(f"Output Project  : {TRAIN_OUT_DIR}")
print(f"Epochs Target   : 10")
print(f"Image Size      : 640")

# Load base model
model = YOLO(base_pt)

# Fine-tune model for EXACTLY 10 EPOCHS on single-class license_plate dataset
t0 = time.time()
results = model.train(
    data=DATASET_YAML,
    epochs=10,
    imgsz=640,
    batch=4,
    patience=10,
    project=os.path.dirname(TRAIN_OUT_DIR),
    name=os.path.basename(TRAIN_OUT_DIR),
    exist_ok=True,
    verbose=True,
)
t1 = time.time()

training_time_sec = round(t1 - t0, 2)
print(f"\n[SUCCESS] 10-Epoch Training completed in {training_time_sec} seconds!")

best_pt_path = os.path.join(TRAIN_OUT_DIR, "weights", "best.pt")
if not os.path.exists(best_pt_path):
    print(f"[ERROR] Trained weights best.pt not found at: {best_pt_path}")
    sys.exit(1)

# Verify single-class metadata of trained best.pt
best_model = YOLO(best_pt_path)
print(f"\n[VERIFICATION] Trained Model Details:")
print(f"  Class Count: {len(best_model.names)}")
print(f"  Class Names: {best_model.names}")

if len(best_model.names) != 1 or best_model.names.get(0) != "license_plate":
    print(f"[ERROR] Expected single class '0: license_plate', got {best_model.names}")
    sys.exit(1)

# Copy best.pt to canonical models/license_plate_detector.pt
os.makedirs(os.path.dirname(CANONICAL_MODEL_PT), exist_ok=True)
shutil.copy(best_pt_path, CANONICAL_MODEL_PT)
print(f"\n[OK] Successfully copied trained model weights:")
print(f"  Source: {best_pt_path}")
print(f"  Target: {CANONICAL_MODEL_PT}")

# Verify active vehicle model is untouched
veh_pt = os.path.join(PROJECT_ROOT, "models", "vehicle_detector.pt")
if os.path.exists(veh_pt):
    v_model = YOLO(veh_pt)
    print(f"\n[VERIFICATION] Vehicle Model (UNTOUCHED):")
    print(f"  Path       : {veh_pt}")
    print(f"  Class Count: {len(v_model.names)}")
    print(f"  Class Names: {v_model.names}")

print("=" * 80)
