import os
import sys
import glob
import cv2

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_DIR = os.path.join(PROJECT_ROOT, "datasets", "license_plate_detection")
OUT_DIR = os.path.join(PROJECT_ROOT, "debug", "license_plate_dataset_samples")

def visualize_dataset():
    print("=" * 80)
    print("        STEP 4: GENERATE VISUAL ANNOTATED DATASET SAMPLES        ")
    print("=" * 80)

    os.makedirs(OUT_DIR, exist_ok=True)

    img_paths = sorted(glob.glob(os.path.join(DATASET_DIR, "**", "images", "*.jpg"), recursive=True))
    print(f"Generating visualizations for {len(img_paths)} dataset samples...")

    saved_count = 0

    for img_p in img_paths:
        bname = os.path.splitext(os.path.basename(img_p))[0]
        # find corresponding label file
        lbl_p = img_p.replace("images", "labels").replace(".jpg", ".txt")

        img = cv2.imread(img_p)
        if img is None or not os.path.exists(lbl_p):
            continue

        h, w = img.shape[:2]

        with open(lbl_p, "r") as lf:
            lines = [l.strip() for l in lf.readlines() if l.strip()]

        vis_img = img.copy()

        for line in lines:
            parts = line.split()
            if len(parts) == 5:
                cid, xc, yc, bw, bh = int(parts[0]), float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])
                
                bx1 = int((xc - bw / 2.0) * w)
                by1 = int((yc - bh / 2.0) * h)
                bx2 = int((xc + bw / 2.0) * w)
                by2 = int((yc + bh / 2.0) * h)

                # Draw green bounding box for license_plate
                cv2.rectangle(vis_img, (bx1, by1), (bx2, by2), (0, 255, 0), 2)
                cv2.putText(vis_img, "license_plate (0)", (bx1, max(15, by1 - 5)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        save_p = os.path.join(OUT_DIR, f"vis_{bname}.jpg")
        cv2.imwrite(save_p, vis_img)
        saved_count += 1

    print(f"[SUCCESS] Saved {saved_count} annotated sample images to '{OUT_DIR}'")
    print("=" * 80)

if __name__ == "__main__":
    visualize_dataset()
