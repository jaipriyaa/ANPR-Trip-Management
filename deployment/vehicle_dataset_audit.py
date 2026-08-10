import os
import glob
import cv2
import yaml
from collections import Counter, defaultdict

def audit_dataset(dataset_dir="dataset images", output_sample_dir="debug/vehicle_dataset_samples"):
    os.makedirs(output_sample_dir, exist_ok=True)
    splits = ["train", "valid", "test"]
    
    print("=" * 60, flush=True)
    print("      VEHICLE DATASET AUDIT REPORT", flush=True)
    print("=" * 60, flush=True)
    
    # 1. Search for data.yaml or configuration files
    yaml_candidates = glob.glob(os.path.join(dataset_dir, "**/*.yaml"), recursive=True) + \
                      glob.glob(os.path.join(dataset_dir, "**/*.yml"), recursive=True) + \
                      glob.glob("*.yaml") + glob.glob("*.yml")
    
    dataset_yaml_data = None
    if yaml_candidates:
        print(f"\n[YAML Config Found]: {yaml_candidates[0]}", flush=True)
        with open(yaml_candidates[0], 'r') as f:
            dataset_yaml_data = yaml.safe_load(f)
            print(yaml.dump(dataset_yaml_data, default_flow_style=False), flush=True)
    else:
        print("\n[YAML Config]: No data.yaml found inside raw dataset directory.", flush=True)

    total_stats = {}
    all_class_counts = defaultdict(Counter)
    class_id_set = set()
    
    # Standard color palette for visualization (BGR)
    colors = [
        (0, 255, 0),    # Class 0: Green
        (255, 0, 0),    # Class 1: Blue
        (0, 0, 255),    # Class 2: Red
        (0, 255, 255),  # Class 3: Yellow
        (255, 0, 255),  # Class 4: Magenta
        (255, 255, 0),  # Class 5: Cyan
        (128, 0, 255),  # Class 6: Purple
        (255, 128, 0)   # Class 7: Orange
    ]

    for split in splits:
        img_dir = os.path.join(dataset_dir, split, "images")
        lbl_dir = os.path.join(dataset_dir, split, "labels")
        
        img_files = glob.glob(os.path.join(img_dir, "*.*"))
        img_files = [f for f in img_files if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.webp'))]
        lbl_files = glob.glob(os.path.join(lbl_dir, "*.txt"))
        
        split_class_counts = Counter()
        annotation_count = 0
        corrupted_images = 0
        invalid_annotations = 0
        out_of_bounds = 0
        missing_labels = 0
        
        img_basename_map = {os.path.splitext(os.path.basename(f))[0]: f for f in img_files}
        lbl_basename_map = {os.path.splitext(os.path.basename(f))[0]: f for f in lbl_files}
        
        sample_drawn_count = 0
        for bname, img_path in img_basename_map.items():
            lbl_path = lbl_basename_map.get(bname)
            if not lbl_path or not os.path.exists(lbl_path):
                missing_labels += 1
                continue
                
            boxes_to_draw = []
            with open(lbl_path, 'r') as lf:
                lines = [line.strip() for line in lf.readlines() if line.strip()]
                
            for line in lines:
                parts = line.split()
                if len(parts) != 5:
                    invalid_annotations += 1
                    continue
                try:
                    cls_id = int(parts[0])
                    xc, yc, bw, bh = map(float, parts[1:])
                    class_id_set.add(cls_id)
                    split_class_counts[cls_id] += 1
                    all_class_counts[split][cls_id] += 1
                    annotation_count += 1
                    
                    if not (0.0 <= xc <= 1.0 and 0.0 <= yc <= 1.0 and 0.0 <= bw <= 1.0 and 0.0 <= bh <= 1.0):
                        out_of_bounds += 1
                        
                    boxes_to_draw.append((cls_id, xc, yc, bw, bh))
                except ValueError:
                    invalid_annotations += 1

            # Visualize first 5 images per split with annotations
            if sample_drawn_count < 5 and boxes_to_draw:
                img = cv2.imread(img_path)
                if img is None:
                    corrupted_images += 1
                    continue
                h, w, _ = img.shape
                sample_drawn_count += 1
                img_vis = img.copy()
                for cls_id, xc, yc, bw, bh in boxes_to_draw:
                    x1 = int((xc - bw / 2) * w)
                    y1 = int((yc - bh / 2) * h)
                    x2 = int((xc + bw / 2) * w)
                    y2 = int((yc + bh / 2) * h)
                    
                    color = colors[cls_id % len(colors)]
                    cls_name = f"Class {cls_id}"
                    if dataset_yaml_data and "names" in dataset_yaml_data:
                        names_data = dataset_yaml_data["names"]
                        if isinstance(names_data, dict):
                            cls_name = names_data.get(cls_id, cls_name)
                        elif isinstance(names_data, list) and cls_id < len(names_data):
                            cls_name = names_data[cls_id]
                            
                    cv2.rectangle(img_vis, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(img_vis, f"{cls_name} ({cls_id})", (x1, max(y1 - 5, 15)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                                
                sample_out_path = os.path.join(output_sample_dir, f"{split}_sample_{sample_drawn_count}_{bname}.jpg")
                cv2.imwrite(sample_out_path, img_vis)

        total_stats[split] = {
            "num_images": len(img_files),
            "num_labels": len(lbl_files),
            "num_annotations": annotation_count,
            "corrupted_images": corrupted_images,
            "missing_labels": missing_labels,
            "invalid_annotations": invalid_annotations,
            "out_of_bounds": out_of_bounds,
            "class_counts": dict(sorted(split_class_counts.items()))
        }

    print("\n" + "=" * 60, flush=True)
    print("SUMMARY STATISTICS", flush=True)
    print("=" * 60, flush=True)
    for split in splits:
        s = total_stats[split]
        print(f"\n[{split.upper()}]", flush=True)
        print(f"  - Number of images       : {s['num_images']}", flush=True)
        print(f"  - Number of label files  : {s['num_labels']}", flush=True)
        print(f"  - Total annotations      : {s['num_annotations']}", flush=True)
        print(f"  - Corrupted images       : {s['corrupted_images']}", flush=True)
        print(f"  - Missing label files    : {s['missing_labels']}", flush=True)
        print(f"  - Invalid annotation lines: {s['invalid_annotations']}", flush=True)
        print(f"  - Out-of-bounds bounding boxes: {s['out_of_bounds']}", flush=True)
        print(f"  - Class annotation breakdown:", flush=True)
        for cid, cnt in s['class_counts'].items():
            print(f"      Class ID {cid}: {cnt} annotations", flush=True)
            
    print("\n" + "=" * 60, flush=True)
    print("ALL CLASS IDs FOUND ACROSS ENTIRE DATASET:", flush=True)
    print("=" * 60, flush=True)
    print(f"Class IDs present: {sorted(list(class_id_set))}", flush=True)
    print(f"Visualizations saved to: {os.path.abspath(output_sample_dir)}", flush=True)
    print("=" * 60, flush=True)
    
    return total_stats, class_id_set, dataset_yaml_data

if __name__ == "__main__":
    audit_dataset()
