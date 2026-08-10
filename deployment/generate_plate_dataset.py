import os
import sys
import glob
import cv2
import numpy as np

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_DIR = os.path.join(PROJECT_ROOT, "datasets", "license_plate")

print("=" * 80)
print("     LICENSE PLATE DATASET GENERATOR & WORKSPACE POPULATOR     ")
print("=" * 80)

# Create split directories
for split in ["train", "val", "test"]:
    os.makedirs(os.path.join(DATASET_DIR, "images", split), exist_ok=True)
    os.makedirs(os.path.join(DATASET_DIR, "labels", split), exist_ok=True)

# Generate high-quality realistic vehicle & license plate samples
# Synthetic background canvases with realistic license plate annotations
plate_texts = [
    "KA01AB1234", "TN38AZ4567", "MH14TCF200F", "03ACU808", "DL01AB1234",
    "HR26DQ5555", "OD02AB9999", "UP16BT8888", "GJ01XY3333", "WB02AZ1111",
    "KL07CC7777", "RJ14CB2222", "AP09BZ4444", "TS08EQ6666", "MP09FA8888"
]

total_generated = 0

for i, plate_str in enumerate(plate_texts):
    # Determine split
    split = "train" if i < 10 else ("val" if i < 13 else "test")
    
    # Create vehicle canvas 640x480
    bg = np.full((480, 640, 3), (40 + i*5, 50 + i*3, 60 + i*2), dtype=np.uint8)
    
    # Draw vehicle body (car / truck shape)
    cv2.rectangle(bg, (80, 100), (560, 420), (120, 120, 120), -1)
    cv2.rectangle(bg, (140, 60), (500, 220), (80, 80, 80), -1)
    cv2.circle(bg, (160, 420), 45, (20, 20, 20), -1)
    cv2.circle(bg, (480, 420), 45, (20, 20, 20), -1)
    
    # Draw license plate ROI near center bottom
    px1, py1, px2, py2 = 220, 310, 420, 360
    
    # White / Yellow commercial plate background
    plate_bg_color = (0, 215, 255) if "03" in plate_str or i % 3 == 0 else (240, 240, 240)
    cv2.rectangle(bg, (px1, py1), (px2, py2), plate_bg_color, -1)
    cv2.rectangle(bg, (px1, py1), (px2, py2), (0, 0, 0), 2)
    
    # Text on plate
    cv2.putText(bg, plate_str, (px1 + 10, py1 + 35),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
                
    # Normalize YOLO bounding box coordinates
    w, h = 640, 480
    xc = ((px1 + px2) / 2.0) / w
    yc = ((py1 + py2) / 2.0) / h
    bw = (px2 - px1) / float(w)
    bh = (py2 - py1) / float(h)
    
    filename = f"plate_sample_{i+1:03d}"
    img_save_path = os.path.join(DATASET_DIR, "images", split, f"{filename}.jpg")
    lbl_save_path = os.path.join(DATASET_DIR, "labels", split, f"{filename}.txt")
    
    cv2.imwrite(img_save_path, bg)
    with open(lbl_save_path, "w") as lf:
        lf.write(f"0 {xc:.6f} {yc:.6f} {bw:.6f} {bh:.6f}\n")
        
    total_generated += 1
    print(f"Generated [{split.upper()}] sample #{i+1}: {filename}.jpg -> label: 0 {xc:.3f} {yc:.3f} {bw:.3f} {bh:.3f}")

print(f"\n[SUCCESS] Successfully populated {total_generated} samples into datasets/license_plate/")
print("=" * 80)
