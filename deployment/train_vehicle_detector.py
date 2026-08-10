import os
import glob
import shutil
import cv2
import yaml
import json
import numpy as np
from pathlib import Path
from ultralytics import YOLO

def train_and_verify_vehicle_detector(
    data_yaml="datasets/vehicle_detection/data.yaml",
    base_model="backend/yolo11n.pt",
    output_model="models/vehicle_detector.pt",
    backup_model="models/vehicle_detector_coco_backup.pt",
    epochs=50,
    imgsz=640,
    patience=10,
    batch=16
):
    print("=" * 70, flush=True)
    print("      PHASE 1-6: VEHICLE DETECTOR TRAINING & VERIFICATION", flush=True)
    print("=" * 70, flush=True)

    # 1. PHASE 2: BACKUP CURRENT COCO MODEL
    if os.path.exists(output_model):
        print(f"Checking current model at {output_model}...", flush=True)
        curr_m = YOLO(output_model)
        num_curr_cls = len(curr_m.names)
        print(f"Current model class count: {num_curr_cls} ({list(curr_m.names.values())[:4]}...)", flush=True)
        if not os.path.exists(backup_model):
            shutil.copy2(output_model, backup_model)
            print(f"Backed up current model to {backup_model}", flush=True)
        else:
            print(f"Backup already exists at {backup_model}", flush=True)

    # 2. PHASE 3: VERIFY DATASET BEFORE TRAINING
    if not os.path.exists(data_yaml):
        raise FileNotFoundError(f"CRITICAL: data.yaml not found at {data_yaml}")
    if not os.path.exists(base_model):
        raise FileNotFoundError(f"CRITICAL: Pretrained base model not found at {base_model}")

    with open(data_yaml, "r") as f:
        yaml_content = yaml.safe_load(f)

    print("\n--- DATASET VERIFICATION ---", flush=True)
    print("data.yaml content:", flush=True)
    print(yaml.dump(yaml_content, default_flow_style=False), flush=True)

    expected_names = {0: "car", 1: "motorcycle", 2: "bus", 3: "truck"}
    if yaml_content.get("nc") != 4 or yaml_content.get("names") != expected_names:
        raise ValueError(f"CRITICAL: data.yaml classes mismatch! Expected nc=4, names={expected_names}")

    dataset_base = yaml_content.get("path", "datasets/vehicle_detection")
    splits = ["train", "valid", "test"]
    split_counts = {}

    for s in splits:
        img_dir = os.path.join(dataset_base, s, "images")
        lbl_dir = os.path.join(dataset_base, s, "labels")
        imgs = glob.glob(os.path.join(img_dir, "*.*"))
        lbls = glob.glob(os.path.join(lbl_dir, "*.txt"))
        
        # Count annotations per class
        cls_ann_count = {0: 0, 1: 0, 2: 0, 3: 0}
        for lp in lbls:
            with open(lp, "r") as lf:
                for line in lf:
                    parts = line.strip().split()
                    if len(parts) >= 5:
                        cid = int(parts[0])
                        if cid in cls_ann_count:
                            cls_ann_count[cid] += 1
                            
        split_counts[s] = {
            "images": len(imgs),
            "labels": len(lbls),
            "class_annotations": cls_ann_count
        }
        print(f"Split '{s}': {len(imgs)} images, {len(lbls)} labels. Annotations: {cls_ann_count}", flush=True)

    # 3. PHASE 4: TRAIN MODEL FOR 50 EPOCHS
    print(f"\nStarting YOLOv11 training for {epochs} epochs (imgsz={imgsz}, batch={batch}, patience={patience})...", flush=True)
    model = YOLO(base_model)

    train_results = model.train(
        data=data_yaml,
        epochs=epochs,
        imgsz=imgsz,
        patience=patience,
        batch=batch,
        optimizer="AdamW",
        project="models",
        name="vehicle_training",
        exist_ok=True,
        workers=4,
        verbose=True,
        mosaic=0.5,
        mixup=0.0,
        scale=0.5,
        degrees=10.0,
        hsv_h=0.015,
        hsv_s=0.7,
        hsv_v=0.4,
        save=True
    )

    # 4. PHASE 5 & 6: SAVE ARTIFACTS & VERIFY FINAL MODEL
    possible_best_paths = [
        os.path.join("models", "vehicle_training", "weights", "best.pt"),
        os.path.join("runs", "detect", "models", "vehicle_training", "weights", "best.pt"),
        os.path.join("runs", "detect", "vehicle_training", "weights", "best.pt")
    ]

    trained_best_pt = None
    for p in possible_best_paths:
        if os.path.exists(p):
            trained_best_pt = p
            break

    if not trained_best_pt:
        raise RuntimeError(f"CRITICAL ERROR: Training finished but best.pt was not found at any expected path: {possible_best_paths}")

    print(f"\nFound trained best weights at: {trained_best_pt}", flush=True)
    os.makedirs("models", exist_ok=True)
    shutil.copy2(trained_best_pt, output_model)
    print(f"Successfully copied trained weights to: {output_model}", flush=True)

    if not os.path.exists(output_model):
        raise FileNotFoundError(f"CRITICAL ERROR: Failed to copy model to {output_model}")

    # Verify final model names & class count
    final_model = YOLO(output_model)
    final_names = final_model.names
    print(f"\nVerifying final model at {output_model}:", flush=True)
    print(f"  Task            : {final_model.task}", flush=True)
    print(f"  Class Count     : {len(final_names)}", flush=True)
    print(f"  Model Names     : {final_names}", flush=True)

    if len(final_names) != 4 or final_names != expected_names:
        raise ValueError(f"CRITICAL ERROR: Final model class count or names invalid! Got {final_names}, expected {expected_names}")

    # 5. PHASE 7 & 8: OFFICIAL TEST VALIDATION & CONFUSION MATRIX
    print("\n" + "=" * 70, flush=True)
    print("      PHASE 7-8: OFFICIAL ULTRALYTICS TEST VALIDATION", flush=True)
    print("=" * 70, flush=True)

    out_val_dir = "debug/vehicle_training_validation"
    os.makedirs(out_val_dir, exist_ok=True)

    val_res = final_model.val(
        data=data_yaml,
        split="test",
        imgsz=imgsz,
        project=out_val_dir,
        name="test_val_run",
        exist_ok=True,
        save_json=True,
        plots=True
    )

    mp = float(val_res.box.mp)
    mr = float(val_res.box.mr)
    map50 = float(val_res.box.map50)
    map50_95 = float(val_res.box.map)

    print("\nOFFICIAL TEST SPLIT METRICS:", flush=True)
    print(f"  Precision (mp) : {mp:.4f}", flush=True)
    print(f"  Recall (mr)    : {mr:.4f}", flush=True)
    print(f"  mAP@50         : {map50:.4f}", flush=True)
    print(f"  mAP@50-95      : {map50_95:.4f}", flush=True)

    print("\nPER-CLASS TEST METRICS:", flush=True)
    per_class_results = {}
    for cid, name in expected_names.items():
        p_val = float(val_res.box.p[cid]) if cid < len(val_res.box.p) else 0.0
        r_val = float(val_res.box.r[cid]) if cid < len(val_res.box.r) else 0.0
        ap50_val = float(val_res.box.ap50[cid]) if cid < len(val_res.box.ap50) else 0.0
        ap_val = float(val_res.box.ap[cid]) if cid < len(val_res.box.ap) else 0.0
        
        per_class_results[name] = {
            "precision": p_val,
            "recall": r_val,
            "mAP50": ap50_val,
            "mAP50-95": ap_val
        }
        print(f"  Class {cid} ({name:10s}): Precision={p_val:.4f}, Recall={r_val:.4f}, mAP50={ap50_val:.4f}, mAP50-95={ap_val:.4f}", flush=True)

    cm_matrix = val_res.confusion_matrix.matrix
    print("\nOFFICIAL CONFUSION MATRIX (5x5):", flush=True)
    print(cm_matrix, flush=True)

    # 6. PHASE 9: VISUAL TEST PREDICTIONS (20 images per class)
    print("\n" + "=" * 70, flush=True)
    print("      PHASE 9: VISUAL TEST PREDICTIONS GENERATION", flush=True)
    print("=" * 70, flush=True)

    for c_name in expected_names.values():
        os.makedirs(os.path.join(out_val_dir, c_name), exist_ok=True)

    test_img_dir = os.path.join(dataset_base, "test", "images")
    test_lbl_dir = os.path.join(dataset_base, "test", "labels")
    test_images = sorted(glob.glob(os.path.join(test_img_dir, "*.*")))

    class_colors = {
        0: (0, 255, 0),     # Car: Green
        1: (255, 100, 0),   # Motorcycle: Blue/Cyan
        2: (0, 0, 255),     # Bus: Red
        3: (0, 255, 255)    # Truck: Yellow
    }

    viz_counts = {0: 0, 1: 0, 2: 0, 3: 0}

    for img_p in test_images:
        bname = Path(img_p).stem
        lbl_p = os.path.join(test_lbl_dir, bname + ".txt")
        gt_boxes = []
        if os.path.exists(lbl_p):
            with open(lbl_p, "r") as f:
                for l in f:
                    parts = l.strip().split()
                    if len(parts) >= 5:
                        gt_boxes.append((int(parts[0]), float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])))

        img = cv2.imread(img_p)
        if img is None:
            continue
        h, w, _ = img.shape
        
        # Inference
        res = final_model.predict(img_p, conf=0.25, verbose=False)[0]
        img_viz = img.copy()

        # Draw GT (gray thin)
        for g_cid, g_xc, g_yc, g_bw, g_bh in gt_boxes:
            gx1 = max(0, int((g_xc - g_bw/2) * w))
            gy1 = max(0, int((g_yc - g_bh/2) * h))
            gx2 = min(w, int((g_xc + g_bw/2) * w))
            gy2 = min(h, int((g_yc + g_bh/2) * h))
            cv2.rectangle(img_viz, (gx1, gy1), (gx2, gy2), (180, 180, 180), 1)
            cv2.putText(img_viz, f"GT:{expected_names[g_cid]}", (gx1, min(gy2+12, h-5)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (180, 180, 180), 1)

        # Draw Preds
        for box in res.boxes:
            px1, py1, px2, py2 = map(int, box.xyxy[0].tolist())
            p_conf = float(box.conf[0])
            p_cid = int(box.cls[0])
            p_cname = expected_names.get(p_cid, "unknown")
            color = class_colors.get(p_cid, (0, 255, 255))
            
            cv2.rectangle(img_viz, (px1, py1), (px2, py2), color, 2)
            cv2.putText(img_viz, f"Pred:{p_cname} {p_conf:.2f}", (px1, max(py1-5, 15)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)

        gt_classes_in_img = set(g[0] for g in gt_boxes)
        for cid in gt_classes_in_img:
            if cid in viz_counts and viz_counts[cid] < 20:
                c_name = expected_names[cid]
                out_p = os.path.join(out_val_dir, c_name, f"test_val_{viz_counts[cid]+1}_{bname}.jpg")
                cv2.imwrite(out_p, img_viz)
                viz_counts[cid] += 1

    print(f"Visual prediction samples saved per class: {viz_counts}", flush=True)

    # Save summary report JSON
    report = {
        "output_model": output_model,
        "backup_model": backup_model,
        "class_mapping": expected_names,
        "dataset_split_counts": split_counts,
        "overall_test_metrics": {
            "precision": mp,
            "recall": mr,
            "mAP50": map50,
            "mAP50_95": map50_95
        },
        "per_class_test_metrics": per_class_results,
        "confusion_matrix_5x5": cm_matrix.tolist(),
        "visual_prediction_counts": viz_counts
    }

    os.makedirs(r"C:\Users\Manoj Kumar\.gemini\antigravity\brain\9e6d53e6-7bf8-4725-aae2-11db59843e26\scratch", exist_ok=True)
    report_json_path = r"C:\Users\Manoj Kumar\.gemini\antigravity\brain\9e6d53e6-7bf8-4725-aae2-11db59843e26\scratch\training_execution_report.json"
    with open(report_json_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\nSaved execution summary report to {report_json_path}", flush=True)
    print("=" * 70, flush=True)
    return report

if __name__ == "__main__":
    train_and_verify_vehicle_detector()
