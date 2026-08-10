import glob, os, cv2
from collections import Counter
from ultralytics import YOLO

print("Loading YOLO11n...", flush=True)
model = YOLO('backend/yolo11n.pt')

saved_counts = {i: 0 for i in range(8)}
crops_by_cls = {i: [] for i in range(8)}

img_files = glob.glob('dataset images/train/images/*.*')
for img_path in img_files:
    bname = os.path.splitext(os.path.basename(img_path))[0]
    lbl_path = os.path.join('dataset images/train/labels', bname + '.txt')
    if not os.path.exists(lbl_path):
        continue
    
    with open(lbl_path) as f:
        lines = f.readlines()
        
    has_needed = False
    for line in lines:
        parts = line.strip().split()
        if len(parts) == 5:
            cid = int(parts[0])
            if cid in saved_counts and saved_counts[cid] < 15:
                has_needed = True
                break
                
    if not has_needed:
        continue

    img = cv2.imread(img_path)
    if img is None:
        continue
    h, w, _ = img.shape
    
    for line in lines:
        parts = line.strip().split()
        if len(parts) == 5:
            cls_id = int(parts[0])
            if cls_id in saved_counts and saved_counts[cls_id] < 15:
                xc, yc, bw, bh = map(float, parts[1:])
                x1 = max(0, int((xc - bw / 2) * w))
                y1 = max(0, int((yc - bh / 2) * h))
                x2 = min(w, int((xc + bw / 2) * w))
                y2 = min(h, int((yc + bh / 2) * h))
                crop = img[y1:y2, x1:x2]
                if crop.size > 0:
                    saved_counts[cls_id] += 1
                    crops_by_cls[cls_id].append(crop)
                    
    if all(cnt >= 15 for cnt in saved_counts.values()):
        break

print(f"Crops collected: {saved_counts}", flush=True)

for cid, crops in crops_by_cls.items():
    pred_counts = Counter()
    for crop in crops:
        res = model(crop, conf=0.15, verbose=False)
        for r in res:
            for box in r.boxes:
                c = int(box.cls[0])
                pred_counts[model.names[c]] += 1
    print(f"Raw Class {cid} ({len(crops)} crops) -> Predictions: {dict(pred_counts)}", flush=True)
