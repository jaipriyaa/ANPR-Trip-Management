import os
import glob
import shutil
import yaml
from collections import Counter

# Raw class mapping:
# 0 -> 0 (car)
# 1 -> 1 (motorcycle)
# 3 -> 2 (bus)
# 2 -> 3 (truck)
# 5 -> 3 (truck)
# 4, 6, 7 -> Exclude

CLASS_MAPPING = {
    0: 0,  # car
    1: 1,  # motorcycle
    3: 2,  # bus
    2: 3,  # truck
    5: 3,  # truck
}

CLASS_NAMES = {
    0: "car",
    1: "motorcycle",
    2: "bus",
    3: "truck"
}

def create_clean_dataset(
    src_dir="dataset images",
    dest_dir="datasets/vehicle_detection"
):
    print("=" * 60)
    print("      CREATING CLEAN VEHICLE DETECTION DATASET")
    print("=" * 60)

    if os.path.exists(dest_dir):
        print(f"Cleaning existing directory: {dest_dir}")
        shutil.rmtree(dest_dir)

    splits = ["train", "valid", "test"]
    stats = {}

    for split in splits:
        src_img_dir = os.path.join(src_dir, split, "images")
        src_lbl_dir = os.path.join(src_dir, split, "labels")

        dest_img_dir = os.path.join(dest_dir, split, "images")
        dest_lbl_dir = os.path.join(dest_dir, split, "labels")

        os.makedirs(dest_img_dir, exist_ok=True)
        os.makedirs(dest_lbl_dir, exist_ok=True)

        img_files = glob.glob(os.path.join(src_img_dir, "*.*"))
        img_files = [f for f in img_files if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.webp'))]

        copied_images = 0
        copied_labels = 0
        converted_annotations = 0
        class_counts = Counter()

        for img_path in img_files:
            bname = os.path.splitext(os.path.basename(img_path))[0]
            lbl_path = os.path.join(src_lbl_dir, bname + ".txt")

            new_lines = []
            if os.path.exists(lbl_path):
                with open(lbl_path, 'r') as lf:
                    for line in lf:
                        parts = line.strip().split()
                        if len(parts) == 5:
                            try:
                                raw_cid = int(parts[0])
                                if raw_cid in CLASS_MAPPING:
                                    new_cid = CLASS_MAPPING[raw_cid]
                                    xc, yc, bw, bh = map(float, parts[1:])
                                    # Ensure bounds [0, 1]
                                    xc = max(0.0, min(1.0, xc))
                                    yc = max(0.0, min(1.0, yc))
                                    bw = max(0.0, min(1.0, bw))
                                    bh = max(0.0, min(1.0, bh))
                                    if bw > 0.0 and bh > 0.0:
                                        new_lines.append(f"{new_cid} {xc:.6f} {yc:.6f} {bw:.6f} {bh:.6f}\n")
                                        class_counts[new_cid] += 1
                                        converted_annotations += 1
                            except ValueError:
                                continue

            # Copy image and write label (keep image even if new_lines is empty as background sample, or write label)
            dest_img_path = os.path.join(dest_img_dir, os.path.basename(img_path))
            dest_lbl_path = os.path.join(dest_lbl_dir, bname + ".txt")

            shutil.copy2(img_path, dest_img_path)
            copied_images += 1

            with open(dest_lbl_path, 'w') as f_out:
                f_out.writelines(new_lines)
            copied_labels += 1

        stats[split] = {
            "images": copied_images,
            "labels": copied_labels,
            "annotations": converted_annotations,
            "class_counts": dict(sorted(class_counts.items()))
        }

    # Write production data.yaml
    data_yaml_content = {
        "path": os.path.abspath(dest_dir).replace("\\", "/"),
        "train": "train/images",
        "val": "valid/images",
        "test": "test/images",
        "nc": 4,
        "names": CLASS_NAMES
    }

    yaml_path = os.path.join(dest_dir, "data.yaml")
    with open(yaml_path, 'w') as f:
        yaml.dump(data_yaml_content, f, default_flow_style=False)

    print("\n[Clean Dataset Created Successfully]")
    for split in splits:
        s = stats[split]
        print(f"\n--- {split.upper()} ---")
        print(f"  Images  : {s['images']}")
        print(f"  Labels  : {s['labels']}")
        print(f"  Annotations: {s['annotations']}")
        print(f"  Class Breakdown:")
        for cid, cnt in s['class_counts'].items():
            print(f"    {cid} ({CLASS_NAMES[cid]}): {cnt}")

    print(f"\nProduction data.yaml written to: {os.path.abspath(yaml_path)}")
    print("=" * 60)
    return stats

if __name__ == "__main__":
    create_clean_dataset()
