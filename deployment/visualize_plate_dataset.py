import os
import sys
import glob
import cv2
import numpy as np

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_DIR = os.path.join(PROJECT_ROOT, "datasets", "license_plate")
OUT_DIR = os.path.join(PROJECT_ROOT, "debug", "plate_dataset_samples")

print("=" * 80)
print("           LICENSE PLATE DATASET VISUALIZATION TOOL (PHASE 6)            ")
print("=" * 80)

os.makedirs(OUT_DIR, exist_ok=True)

samples_generated = 0

for split in ["train", "val", "test"]:
    img_dir = os.path.join(DATASET_DIR, "images", split)
    lbl_dir = os.path.join(DATASET_DIR, "labels", split)
    
    img_files = glob.glob(os.path.join(img_dir, "*.[jJ][pP][gG]")) + \
                glob.glob(os.path.join(img_dir, "*.[jJ][pP][eE][gG]")) + \
                glob.glob(os.path.join(img_dir, "*.[pP][nN][gG]"))
                
    for img_path in img_files[:10]:
        base_name = os.path.splitext(os.path.basename(img_path))[0]
        lbl_path = os.path.join(lbl_dir, f"{base_name}.txt")
        
        img = cv2.imread(img_path)
        if img is None:
            continue
            
        h, w = img.shape[:2]
        
        if os.path.exists(lbl_path):
            with open(lbl_path, "r") as lf:
                lines = [l.strip() for l in lf if l.strip()]
                
            for line in lines:
                parts = line.split()
                if len(parts) == 5:
                    cls_id = int(parts[0])
                    xc, yc, bw, bh = map(float, parts[1:])
                    
                    x1 = int((xc - bw / 2.0) * w)
                    y1 = int((yc - bh / 2.0) * h)
                    x2 = int((xc + bw / 2.0) * w)
                    y2 = int((yc + bh / 2.0) * h)
                    
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 255), 2)
                    cv2.putText(img, f"license_plate", (x1, max(15, y1 - 5)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
                                
        out_path = os.path.join(OUT_DIR, f"{split}_{base_name}_sample.jpg")
        cv2.imwrite(out_path, img)
        samples_generated += 1
        print(f"Saved dataset visualization sample: {out_path}")

print(f"\n[SUMMARY] Total samples generated in debug/plate_dataset_samples/: {samples_generated}")
print("=" * 80)
