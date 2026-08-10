import os
import sys
import glob
import cv2

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_DIR = os.path.join(PROJECT_ROOT, "datasets", "license_plate_detection")

def validate_dataset():
    print("=" * 80)
    print("           STEP 3: LICENSE PLATE DATASET ANNOTATION AUDIT           ")
    print("=" * 80)

    if not os.path.exists(DATASET_DIR):
        print(f"[ERROR] Dataset directory not found: {DATASET_DIR}")
        sys.exit(1)

    splits = ["train", "valid", "test"]
    total_images = 0
    total_labels = 0
    total_boxes = 0
    errors = []

    for split in splits:
        img_dir = os.path.join(DATASET_DIR, split, "images")
        lbl_dir = os.path.join(DATASET_DIR, split, "labels")

        images = sorted(glob.glob(os.path.join(img_dir, "*.*")))
        labels = sorted(glob.glob(os.path.join(lbl_dir, "*.txt")))

        print(f"\n--- Audit Split: [{split.upper()}] ---")
        print(f"  Images count : {len(images)}")
        print(f"  Labels count : {len(labels)}")

        total_images += len(images)
        total_labels += len(labels)

        for img_p in images:
            bname = os.path.splitext(os.path.basename(img_p))[0]
            lbl_p = os.path.join(lbl_dir, f"{bname}.txt")

            # Check image readability
            img = cv2.imread(img_p)
            if img is None:
                errors.append(f"[{split}] Corrupted image file: {img_p}")
                continue

            h, w = img.shape[:2]

            # Check label existence
            if not os.path.exists(lbl_p):
                errors.append(f"[{split}] Missing label file for image: {img_p}")
                continue

            with open(lbl_p, "r") as lf:
                lines = [l.strip() for l in lf.readlines() if l.strip()]

            if not lines:
                errors.append(f"[{split}] Empty label file: {lbl_p}")
                continue

            for l_idx, line in enumerate(lines):
                parts = line.split()
                if len(parts) != 5:
                    errors.append(f"[{split}] Malformed line {l_idx+1} in {lbl_p}: '{line}'")
                    continue

                try:
                    cid = int(parts[0])
                    xc, yc, bw, bh = map(float, parts[1:])
                except ValueError:
                    errors.append(f"[{split}] Non-numeric values in {lbl_p}: '{line}'")
                    continue

                if cid != 0:
                    errors.append(f"[{split}] Invalid class_id={cid} in {lbl_p} (Must be 0 for license_plate)")

                if not (0.0 <= xc <= 1.0 and 0.0 <= yc <= 1.0 and 0.0 < bw <= 1.0 and 0.0 < bh <= 1.0):
                    errors.append(f"[{split}] Out of bounds bbox coordinates in {lbl_p}: '{line}'")

                # Check edge boundaries
                x1 = (xc - bw / 2.0) * w
                y1 = (yc - bh / 2.0) * h
                x2 = (xc + bw / 2.0) * w
                y2 = (yc + bh / 2.0) * h

                if x1 < 0 or y1 < 0 or x2 > w + 1 or y2 > h + 1:
                    errors.append(f"[{split}] BBox extends outside canvas in {lbl_p}: [{x1:.1f}, {y1:.1f}, {x2:.1f}, {y2:.1f}] for {w}x{h}")

                total_boxes += 1

    print("\n----------------------------------------------------------------------")
    print(f"AUDIT SUMMARY: Total Images={total_images}, Total Labels={total_labels}, Total Boxes={total_boxes}")
    if errors:
        print(f"[FAILED] Found {len(errors)} validation errors:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("[SUCCESS] All images, labels, class IDs (0), and bounding boxes are 100% VALID!")
        print("=" * 80)

if __name__ == "__main__":
    validate_dataset()
