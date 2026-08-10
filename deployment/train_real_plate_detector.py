import os
import sys
import shutil
import time
import torch

# Optimize PyTorch CPU threading
torch.set_num_threads(os.cpu_count() or 8)

from ultralytics import YOLO

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_YAML = os.path.join(PROJECT_ROOT, "datasets", "license_plate_detection", "data.yaml")
BASE_MODEL_PT = os.path.join(PROJECT_ROOT, "backend", "yolo11n.pt")
TRAIN_OUT_DIR = os.path.join(PROJECT_ROOT, "models", "license_plate_training")

print("=" * 80)
print("     STEP 4: TRAIN YOLOv11 DEDICATED LICENSE PLATE DETECTOR (10 EPOCHS)     ")
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
print(f"CPU Threads     : {torch.get_num_threads()}")

# Load base model
model = YOLO(base_pt)

# Fine-tune model for EXACTLY 10 EPOCHS on 833 real-world license plate samples
t0 = time.time()
results = model.train(
    data=DATASET_YAML,
    epochs=10,
    imgsz=640,
    batch=16,
    workers=2,
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

best_model = YOLO(best_pt_path)
print(f"\n[VERIFICATION] Trained Model Details:")
print(f"  Class Count: {len(best_model.names)}")
print(f"  Class Names: {best_model.names}")
print(f"  Best Pt Path: {best_pt_path}")

print("=" * 80)
