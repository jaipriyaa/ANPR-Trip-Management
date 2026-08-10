import os
import sys
import glob
import shutil
import cv2

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(PROJECT_ROOT, "dataset plates")
TARGET_DIR = os.path.join(PROJECT_ROOT, "datasets", "license_plate_detection")
SAMPLES_DIR = os.path.join(PROJECT_ROOT, "debug", "license_plate_dataset_samples")

def populate_dataset():
    print("=" * 80)
    print("      STEP 2 & 3: CREATE PRODUCTION DATASET & VISUAL SAMPLES      ")
    print("=" * 80)

    # 1. Create clean folder structure
    splits = ["train", "val", "test"]
    for split in splits:
        os.makedirs(os.path.join(TARGET_DIR, "images", split), exist_ok=True)
        os.makedirs(os.path.join(TARGET_DIR, "labels", split), exist_ok=True)

    os.makedirs(SAMPLES_DIR, exist_ok=True)

    # 2. Write data.yaml
    yaml_content = """path: datasets/license_plate_detection
train: images/train
val: images/val
test: images/test

nc: 1

names:
  0: license_plate
"""
    yaml_path = os.path.join(TARGET_DIR, "data.yaml")
    with open(yaml_path, "w", encoding="utf-8") as f:
        f.write(yaml_content)

    print(f"[OK] Created data.yaml at {yaml_path}")

    # Map source split folder names -> target split folder names
    split_map = {
        "train": "train",
        "valid": "val",
        "test": "test"
    }

    copied_images = 0
    copied_labels = 0

    for src_split, target_split in split_map.items():
        src_img_dir = os.path.join(SRC_DIR, src_split, "images")
        src_lbl_dir = os.path.join(SRC_DIR, src_split, "labels")

        dest_img_dir = os.path.join(TARGET_DIR, "images", target_split)
        dest_lbl_dir = os.path.join(TARGET_DIR, "labels", target_split)

        imgs = sorted(glob.glob(os.path.join(src_img_dir, "*.*")))
        for img_p in imgs:
            fname = os.path.basename(img_p)
            bname = os.path.splitext(fname)[0]
            lbl_p = os.path.join(src_lbl_dir, f"{bname}.txt")

            shutil.copy(img_p, os.path.join(dest_img_dir, fname))
            copied_images += 1

            if os.path.exists(lbl_p):
                shutil.copy(lbl_p, os.path.join(dest_lbl_dir, f"{bname}.txt"))
                copied_labels += 1

    print(f"[OK] Copied {copied_images} images and {copied_labels} labels to {TARGET_DIR}")

    # 3. Generate 30 representative visual ground-truth samples
    sample_imgs = sorted(glob.glob(os.path.join(TARGET_DIR, "images", "train", "*.*")))[:35]
    saved_samples = 0

    for s_img_p in sample_imgs:
        fname = os.path.basename(s_img_p)
        bname = os.path.splitext(fname)[0]
        s_lbl_p = os.path.join(TARGET_DIR, "labels", "train", f"{bname}.txt")

        s_img = cv2.imread(s_img_p)
        if s_img is None or not os.path.exists(s_lbl_p):
            continue

        h, w = s_img.shape[:2]
        with open(s_lbl_p, "r", encoding="utf-8") as lf:
            lines = [l.strip() for l in lf.readlines() if l.strip()]

        vis_img = s_img.copy()
        for line in lines:
            parts = line.split()
            if len(parts) == 5:
                cid, xc, yc, bw, bh = int(parts[0]), float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])
                bx1 = int((xc - bw / 2.0) * w)
                by1 = int((yc - bh / 2.0) * h)
                bx2 = int((xc + bw / 2.0) * w)
                by2 = int((yc + bh / 2.0) * h)

                cv2.rectangle(vis_img, (bx1, by1), (bx2, by2), (0, 255, 0), 2)
                cv2.putText(vis_img, "license_plate", (bx1, max(15, by1 - 5)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        cv2.imwrite(os.path.join(SAMPLES_DIR, f"sample_{bname}.jpg"), vis_img)
        saved_samples += 1

    print(f"[OK] Generated {saved_samples} visual ground-truth sample images in {SAMPLES_DIR}")
    print("=" * 80)

if __name__ == "__main__":
    populate_dataset()
