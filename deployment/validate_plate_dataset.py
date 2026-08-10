import os
import sys
import glob
import cv2
import yaml

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_DIR = os.path.join(PROJECT_ROOT, "datasets", "license_plate")
DATA_YAML_PATH = os.path.join(DATASET_DIR, "data.yaml")

print("=" * 80)
print("             LICENSE PLATE DATASET VALIDATION TOOL (PHASE 5)             ")
print("=" * 80)

if not os.path.exists(DATA_YAML_PATH):
    print(f"[FAIL] data.yaml not found at: {DATA_YAML_PATH}")
    sys.exit(1)

with open(DATA_YAML_PATH, "r") as f:
    data_config = yaml.safe_load(f)

print(f"Loaded config: {data_config}")

total_images = 0
total_labels = 0
total_boxes = 0
invalid_boxes = 0
corrupt_images = 0
missing_labels = 0

split_stats = {}

for split in ["train", "val", "test"]:
    img_dir = os.path.join(DATASET_DIR, "images", split)
    lbl_dir = os.path.join(DATASET_DIR, "labels", split)
    
    os.makedirs(img_dir, exist_ok=True)
    os.makedirs(lbl_dir, exist_ok=True)
    
    img_files = glob.glob(os.path.join(img_dir, "*.[jJ][pP][gG]")) + \
                glob.glob(os.path.join(img_dir, "*.[jJ][pP][eE][gG]")) + \
                glob.glob(os.path.join(img_dir, "*.[pP][nN][gG]"))
                
    split_imgs = len(img_files)
    split_lbls = 0
    split_boxes = 0
    
    for img_path in img_files:
        total_images += 1
        base_name = os.path.splitext(os.path.basename(img_path))[0]
        lbl_path = os.path.join(lbl_dir, f"{base_name}.txt")
        
        # 1. Verify image loading
        img = cv2.imread(img_path)
        if img is None:
            print(f"[CORRUPT IMAGE] {img_path}")
            corrupt_images += 1
            continue
            
        # 2. Check corresponding label file
        if not os.path.exists(lbl_path):
            missing_labels += 1
            continue
            
        split_lbls += 1
        total_labels += 1
        
        # 3. Inspect label content
        with open(lbl_path, "r") as lf:
            lines = [line.strip() for line in lf if line.strip()]
            
        for line in lines:
            parts = line.split()
            if len(parts) != 5:
                print(f"[INVALID SYNTAX] {lbl_path}: line '{line}'")
                invalid_boxes += 1
                continue
                
            try:
                cls_id = int(parts[0])
                xc, yc, w, h = map(float, parts[1:])
                
                if cls_id != 0:
                    print(f"[INVALID CLASS ID] {lbl_path}: class_id {cls_id} != 0")
                    invalid_boxes += 1
                    
                if not (0.0 <= xc <= 1.0 and 0.0 <= yc <= 1.0 and 0.0 < w <= 1.0 and 0.0 < h <= 1.0):
                    print(f"[INVALID BBOX BOUNDS] {lbl_path}: {xc}, {yc}, {w}, {h}")
                    invalid_boxes += 1
                else:
                    split_boxes += 1
                    total_boxes += 1
            except ValueError:
                print(f"[NON-NUMERIC VALUE] {lbl_path}: line '{line}'")
                invalid_boxes += 1

    split_stats[split] = {
        "images": split_imgs,
        "labels": split_lbls,
        "boxes": split_boxes,
    }

print("\n" + "-" * 60)
print("LICENSE PLATE DATASET VALIDATION REPORT")
print("-" * 60)
print(f"{'SPLIT':<15} | {'IMAGES':<10} | {'LABELS':<10} | {'BOXES':<10}")
print("-" * 60)
for split, s in split_stats.items():
    print(f"{split:<15} | {s['images']:<10} | {s['labels']:<10} | {s['boxes']:<10}")
print("-" * 60)
print(f"Total Images   : {total_images}")
print(f"Total Labels   : {total_labels}")
print(f"Total BBoxes   : {total_boxes}")
print(f"Corrupt Images : {corrupt_images}")
print(f"Invalid BBoxes : {invalid_boxes}")
print(f"Missing Labels : {missing_labels}")
print(f"Classes        : 0 = license_plate")

status = "PASS" if (total_images > 0 and corrupt_images == 0 and invalid_boxes == 0) else "NO_DATA / FAIL"
print("-" * 60)
print(f"DATASET VALIDATION STATUS: {status}")
print("=" * 80)
