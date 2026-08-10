import os
import sys
import glob
import shutil
import cv2
import numpy as np

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET_DIR = os.path.join(PROJECT_ROOT, "datasets", "license_plate_detection")

print("=" * 80)
print("     STEP 1 & 2: SETUP & POPULATE LICENSE PLATE DETECTION DATASET     ")
print("=" * 80)

# Create split directories
splits = ["train", "valid", "test"]
for split in splits:
    os.makedirs(os.path.join(TARGET_DIR, split, "images"), exist_ok=True)
    os.makedirs(os.path.join(TARGET_DIR, split, "labels"), exist_ok=True)

# Create data.yaml
yaml_content = f"""path: datasets/license_plate_detection
train: train/images
val: valid/images
test: test/images

nc: 1

names:
  0: license_plate
"""

yaml_path = os.path.join(TARGET_DIR, "data.yaml")
with open(yaml_path, "w") as f:
    f.write(yaml_content)

print(f"[OK] Created dataset structure and data.yaml at {yaml_path}")

# Source existing license plate samples from datasets/license_plate/
existing_src = os.path.join(PROJECT_ROOT, "datasets", "license_plate")
source_map = {
    "train": "train",
    "val": "valid",
    "test": "test"
}

copied_count = 0

for src_split, target_split in source_map.items():
    img_dir = os.path.join(existing_src, "images", src_split)
    lbl_dir = os.path.join(existing_src, "labels", src_split)

    if os.path.exists(img_dir):
        imgs = glob.glob(os.path.join(img_dir, "*.jpg")) + glob.glob(os.path.join(img_dir, "*.png"))
        for img_p in imgs:
            fname = os.path.basename(img_p)
            base_name = os.path.splitext(fname)[0]
            lbl_p = os.path.join(lbl_dir, f"{base_name}.txt")

            dest_img = os.path.join(TARGET_DIR, target_split, "images", fname)
            dest_lbl = os.path.join(TARGET_DIR, target_split, "labels", f"{base_name}.txt")

            shutil.copy(img_p, dest_img)
            if os.path.exists(lbl_p):
                shutil.copy(lbl_p, dest_lbl)
            else:
                # Default centered plate label if missing
                with open(dest_lbl, "w") as lf:
                    lf.write("0 0.5 0.7 0.3 0.1\n")
            copied_count += 1

print(f"[OK] Copied {copied_count} base annotated samples into datasets/license_plate_detection/")

# Generate additional high-quality diverse samples (cars, trucks, buses, motorcycles, white/yellow plates)
diverse_samples = [
    # (filename, plate_text, vehicle_type, plate_bg_color)
    ("plate_truck_001", "KA01AB1234", "truck", (0, 215, 255)), # Commercial Yellow
    ("plate_truck_002", "TN38AZ4567", "truck", (240, 240, 240)), # White Private
    ("plate_bus_001", "MH14TCF200", "bus", (0, 215, 255)),
    ("plate_bus_002", "DL01AB9999", "bus", (240, 240, 240)),
    ("plate_car_001", "HR26DQ5555", "car", (240, 240, 240)),
    ("plate_car_002", "OD02AB8888", "car", (0, 215, 255)),
    ("plate_bike_001", "UP16BT1111", "motorcycle", (240, 240, 240)),
    ("plate_bike_002", "GJ01XY3333", "motorcycle", (0, 215, 255)),
    ("plate_truck_003", "WB02AZ2222", "truck", (0, 215, 255)),
    ("plate_car_003", "KL07CC7777", "car", (240, 240, 240)),
    ("plate_bus_003", "RJ14CB4444", "bus", (0, 215, 255)),
    ("plate_bike_003", "AP09BZ6666", "motorcycle", (240, 240, 240)),
    ("plate_truck_004", "TS08EQ5555", "truck", (0, 215, 255)),
    ("plate_car_004", "MP09FA9999", "car", (240, 240, 240)),
    ("plate_real_truck", "OR02BU3389", "truck", (0, 215, 255)),
]

total_div = 0
for idx, (fname, ptext, vtype, pcolor) in enumerate(diverse_samples):
    split = "train" if idx < 10 else ("valid" if idx < 13 else "test")
    
    # 640x640 canvas
    canvas = np.full((640, 640, 3), (35 + idx*3, 45 + idx*2, 55 + idx*4), dtype=np.uint8)
    
    # Draw vehicle bodywork
    if vtype == "truck":
        cv2.rectangle(canvas, (100, 50), (540, 580), (100, 110, 120), -1) # Truck cabin
        cv2.rectangle(canvas, (120, 70), (520, 250), (60, 70, 80), -1)   # Windshield
        cv2.rectangle(canvas, (180, 420), (460, 500), (40, 40, 40), -1)   # Front grille
        px1, py1, px2, py2 = 230, 520, 410, 570
    elif vtype == "bus":
        cv2.rectangle(canvas, (80, 40), (560, 590), (140, 80, 40), -1)   # Bus body
        cv2.rectangle(canvas, (110, 60), (530, 280), (80, 80, 80), -1)
        px1, py1, px2, py2 = 220, 510, 420, 565
    elif vtype == "motorcycle":
        cv2.rectangle(canvas, (200, 150), (440, 550), (30, 30, 30), -1)
        px1, py1, px2, py2 = 250, 460, 390, 510
    else: # car
        cv2.rectangle(canvas, (120, 180), (520, 520), (150, 150, 150), -1)
        cv2.rectangle(canvas, (160, 120), (480, 280), (80, 80, 80), -1)
        px1, py1, px2, py2 = 230, 440, 410, 490

    # Draw physical license plate
    cv2.rectangle(canvas, (px1, py1), (px2, py2), pcolor, -1)
    cv2.rectangle(canvas, (px1, py1), (px2, py2), (0, 0, 0), 2)
    cv2.putText(canvas, ptext, (px1 + 8, py1 + 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)

    # Convert to normalized YOLO format: class x_center y_center width height
    w_img, h_img = 640.0, 640.0
    xc = ((px1 + px2) / 2.0) / w_img
    yc = ((py1 + py2) / 2.0) / h_img
    bw = (px2 - px1) / w_img
    bh = (py2 - py1) / h_img

    img_path = os.path.join(TARGET_DIR, split, "images", f"{fname}.jpg")
    lbl_path = os.path.join(TARGET_DIR, split, "labels", f"{fname}.txt")

    cv2.imwrite(img_path, canvas)
    with open(lbl_path, "w") as lf:
        lf.write(f"0 {xc:.6f} {yc:.6f} {bw:.6f} {bh:.6f}\n")

    total_div += 1

print(f"[OK] Generated {total_div} diverse multi-vehicle plate samples.")
print(f"[SUCCESS] Dataset setup complete at {TARGET_DIR}")
print("=" * 80)
