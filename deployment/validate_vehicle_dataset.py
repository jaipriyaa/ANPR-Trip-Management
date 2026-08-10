import os
import glob
import yaml
import sys

def validate_dataset(dataset_dir="datasets/vehicle_detection"):
    print("=" * 60, flush=True)
    print("      VALIDATING CLEAN VEHICLE DETECTION DATASET", flush=True)
    print("=" * 60, flush=True)

    yaml_path = os.path.join(dataset_dir, "data.yaml")
    if not os.path.exists(yaml_path):
        print(f"[ERROR] data.yaml not found at: {yaml_path}", flush=True)
        sys.exit(1)

    with open(yaml_path, 'r') as f:
        data_cfg = yaml.safe_load(f)

    print(f"data.yaml path: {yaml_path}", flush=True)
    print(f"Num classes (nc): {data_cfg.get('nc')}", flush=True)
    print(f"Class names: {data_cfg.get('names')}", flush=True)

    if data_cfg.get('nc') != 4:
        print(f"[ERROR] nc must be exactly 4, found: {data_cfg.get('nc')}", flush=True)
        sys.exit(1)

    expected_names = {0: "car", 1: "motorcycle", 2: "bus", 3: "truck"}
    actual_names = data_cfg.get('names')
    if isinstance(actual_names, list):
        actual_names = {i: name for i, name in enumerate(actual_names)}
    
    if actual_names != expected_names:
        print(f"[ERROR] Class names mismatch. Expected {expected_names}, got {actual_names}", flush=True)
        sys.exit(1)

    splits = ["train", "valid", "test"]
    valid_class_ids = {0, 1, 2, 3}
    errors = []

    for split in splits:
        img_dir = os.path.join(dataset_dir, split, "images")
        lbl_dir = os.path.join(dataset_dir, split, "labels")

        if not os.path.exists(img_dir):
            errors.append(f"Missing images directory for split: {split}")
            continue
        if not os.path.exists(lbl_dir):
            errors.append(f"Missing labels directory for split: {split}")
            continue

        img_files = glob.glob(os.path.join(img_dir, "*.*"))
        img_files = [f for f in img_files if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.webp'))]
        lbl_files = glob.glob(os.path.join(lbl_dir, "*.txt"))

        print(f"\n[{split.upper()}] Checking {len(img_files)} images and {len(lbl_files)} label files...", flush=True)

        if len(img_files) == 0:
            errors.append(f"Split {split} has 0 images.")

        img_bnames = {os.path.splitext(os.path.basename(f))[0] for f in img_files}
        lbl_bnames = {os.path.splitext(os.path.basename(f))[0] for f in lbl_files}

        missing_lbls = img_bnames - lbl_bnames
        if missing_lbls:
            errors.append(f"Split {split}: {len(missing_lbls)} images are missing label files.")

        split_boxes = 0
        for img_path in img_files:
            bname = os.path.splitext(os.path.basename(img_path))[0]
            lbl_path = os.path.join(lbl_dir, bname + ".txt")

            if os.path.exists(lbl_path):
                with open(lbl_path, 'r') as lf:
                    lines = [l.strip() for l in lf.readlines() if l.strip()]

                for line_idx, line in enumerate(lines, 1):
                    parts = line.split()
                    if len(parts) != 5:
                        errors.append(f"Split {split}, {bname}.txt: Line {line_idx} does not have 5 fields.")
                        continue
                    try:
                        cls_id = int(parts[0])
                        xc, yc, bw, bh = map(float, parts[1:])

                        if cls_id not in valid_class_ids:
                            errors.append(f"Split {split}, {bname}.txt: Invalid class ID {cls_id}. Allowed: {valid_class_ids}")

                        if not (0.0 <= xc <= 1.0):
                            errors.append(f"Split {split}, {bname}.txt: x_center {xc} outside [0, 1]")
                        if not (0.0 <= yc <= 1.0):
                            errors.append(f"Split {split}, {bname}.txt: y_center {yc} outside [0, 1]")
                        if not (0.0 < bw <= 1.0):
                            errors.append(f"Split {split}, {bname}.txt: width {bw} invalid or non-positive")
                        if not (0.0 < bh <= 1.0):
                            errors.append(f"Split {split}, {bname}.txt: height {bh} invalid or non-positive")

                        split_boxes += 1
                    except ValueError:
                        errors.append(f"Split {split}, {bname}.txt: Line {line_idx} formatting error")

        print(f"[{split.upper()}] Verified {split_boxes} bounding boxes.", flush=True)

    print("\n" + "=" * 60, flush=True)
    if errors:
        print(f"[VALIDATION FAILED] Found {len(errors)} errors:", flush=True)
        for err in errors[:20]:
            print(f"  - {err}", flush=True)
        if len(errors) > 20:
            print(f"  ... and {len(errors) - 20} more errors.", flush=True)
        print("=" * 60, flush=True)
        sys.exit(1)
    else:
        print("[VALIDATION SUCCESSFUL] Clean dataset passed all verification checks!", flush=True)
        print("=" * 60, flush=True)

if __name__ == "__main__":
    validate_dataset()
