import os
import sys
import shutil
import time
from ultralytics import YOLO

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_YAML = os.path.join(PROJECT_ROOT, "datasets", "license_plate", "data.yaml")
BASE_MODEL_PT = os.path.join(PROJECT_ROOT, "backend", "yolo11n.pt")
TRAIN_OUT_DIR = os.path.join(PROJECT_ROOT, "models", "license_plate_training")
CANONICAL_MODEL_PT = os.path.join(PROJECT_ROOT, "models", "license_plate_detector.pt")

print("=" * 80)
print("     YOLOv11 DEDICATED LICENSE PLATE DETECTOR TRAINING TOOL     ")
print("=" * 80)

if not os.path.exists(DATASET_YAML):
    print(f"[ERROR] Dataset yaml not found: {DATASET_YAML}")
    sys.exit(1)

print(f"Base Checkpoint : {BASE_MODEL_PT}")
print(f"Dataset YAML    : {DATASET_YAML}")
print(f"Output Dir      : {TRAIN_OUT_DIR}")

# Load base pretrained model
model = YOLO(BASE_MODEL_PT if os.path.exists(BASE_MODEL_PT) else "yolo11n.pt")

# Fine-tune model on single-class license_plate dataset
t0 = time.time()
results = model.train(
    data=DATASET_YAML,
    epochs=5,
    imgsz=640,
    batch=4,
    device="cpu",
    project=os.path.dirname(TRAIN_OUT_DIR),
    name=os.path.basename(TRAIN_OUT_DIR),
    exist_ok=True,
    verbose=True,
)
t1 = time.time()

training_time_sec = round(t1 - t0, 2)
print(f"\n[SUCCESS] Fine-tuning completed in {training_time_sec} seconds!")

best_pt_path = os.path.join(TRAIN_OUT_DIR, "weights", "best.pt")
if os.path.exists(best_pt_path):
    shutil.copy(best_pt_path, CANONICAL_MODEL_PT)
    print(f"Copied fine-tuned best.pt -> {CANONICAL_MODEL_PT}")
else:
    print(f"[WARNING] best.pt not found at {best_pt_path}")

print("=" * 80)
