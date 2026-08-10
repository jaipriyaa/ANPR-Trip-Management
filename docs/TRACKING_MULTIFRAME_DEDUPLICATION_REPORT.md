# VEHICLE TRACKING, MULTI-FRAME FUSION & DEDUPLICATION REPORT

**Project:** ANPR Trip Management System  
**Module:** Production AI Video & Image ANPR Engine  
**Execution Timestamp:** 2026-08-09T23:45:00+05:30  

---

## 1. Existing Tracker Found
- **File Location:** [`backend/app/ai/vehicle_detector/tracker.py`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/backend/app/ai/vehicle_detector/tracker.py)
- **Class Name:** `VehicleTracker` (IoU-based tracker assigning `tracking_id` e.g., `TRACK-1`, `TRACK-2`, `TEMP-001`).
- **Integration:** Used directly in [`backend/app/ai/inference/video_pipeline.py`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/backend/app/ai/inference/video_pipeline.py) and [`backend/app/ai/video_processor.py`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/backend/app/ai/video_processor.py). No duplicate tracker class was created.

---

## 2. Key Changes Made
1. **Configurable Multi-Frame & Tracking Parameters:** Added explicit configuration parameters to [`backend/app/ai/config/__init__.py`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/backend/app/ai/config/__init__.py):
   - `TRACKING_ENABLED = True`
   - `TRACK_MAX_AGE_SECONDS = 2.0`
   - `MULTIFRAME_ENABLED = True`
   - `MULTIFRAME_WINDOW_SECONDS = 5.0`
   - `MULTIFRAME_MIN_OBSERVATIONS = 2`
   - `MULTIFRAME_SIMILARITY_THRESHOLD = 0.85`
   - `MULTIFRAME_MIN_CONFIDENCE = 0.70`
   - `ENTRY_DEDUP_WINDOW_SECONDS = 120.0`
   - `FUSION_MIN_FRAMES = 2`
   - `FUSION_MIN_CONFIDENCE = 0.70`
   - `FUSION_WEIGHT_CONFIDENCE = 0.60`
   - `FUSION_WEIGHT_FREQUENCY = 0.40`
2. **Multi-Factor Candidate Score Fusion Engine:** Enhanced [`backend/app/ai/postprocessing/fusion.py`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/backend/app/ai/postprocessing/fusion.py) to calculate deterministic candidate scores:
   \[
   \text{Score} = (\text{OCR\_conf} \times 0.35) + (\text{Detector\_conf} \times 0.25) + (\text{Repetition\_ratio} \times 0.20) + (\text{Validation\_score} \times 0.20)
   \]
3. **Database Event Deduplication Protection:** Enforced `ENTRY_DEDUP_WINDOW_SECONDS = 120` in `EntryExitEngine.process_recognition_event()` ([`backend/app/services/entry_exit_service.py`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/backend/app/services/entry_exit_service.py)). Repeated recognitions within 120s return the existing movement record without inserting duplicate database rows.
4. **Mandatory Test Suite:** Implemented 12 comprehensive test cases in [`tests/test_tracking_fusion_dedup.py`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/tests/test_tracking_fusion_dedup.py).

---

## 3. Tracking Algorithm Used
- **Algorithm:** Bounding Box Centroid IoU Tracker (`VehicleTracker`).
- **Parameters:** IoU threshold = `0.30`, Max Age = `30 frames` (`2.0s`).
- **Vehicle-Plate Association:** Plate detection and crop extraction are strictly bound inside each vehicle's `vehicle_bbox` ROI, guaranteeing distinct vehicles (e.g. Track 17 vs Track 18) remain completely independent.

---

## 4. Track Lifecycle
1. **DETECTED:** Vehicle bounding box detected in frame.
2. **TRACKING:** IoU matcher associates detection with active `Tracklet` (or spawns new `TRACK-N`).
3. **PLATE OBSERVATION:** Plate candidate bounding boxes cropped and stored inside tracklet `plate_observations`.
4. **MULTI-FRAME FUSION:** Multi-factor score fusion pools OCR predictions across sampled frames.
5. **VALIDATED:** Candidate normalized and confirmed against Indian registration format (`IndianPlateValidator`).
6. **ENTRY EVENT CREATED:** Exactly **ONE** `VehicleMovement` database event generated per vehicle tracklet.
7. **TRACK CLOSED:** Stale tracks purged after `TRACK_MAX_AGE_SECONDS`.

---

## 5. Multi-Frame Fusion Logic
- Collects OCR candidates across video frames.
- Applies positional character-level majority voting and Indian plate format reordering (handling two-line inverted plate text).
- Rejects blacklisted container/body advertising terms (`GOODS`, `CARRIER`, `LOGISTICS`, `ASHOK`, `LEYLAND`, `TATA`, etc.).

---

## 6. Plate Similarity & Character Confusion Logic
- Handles OCR confusions: `0 ↔ O`, `1 ↔ I`, `2 ↔ Z`, `5 ↔ S`, `6 ↔ G`, `8 ↔ B`.
- Substitutions are evaluated positionally against Indian plate patterns (`[A-Z]{2}\d{1,2}[A-Z]{1,3}\d{4}`).

---

## 7. Deduplication Logic
- Video pipeline aggregates 100+ frame detections of a physical vehicle into **1 tracklet payload**.
- `EntryExitEngine` checks gate/camera duplicate suppression window (`120s`), preventing duplicate row insertion into PostgreSQL/SQLite.

---

## 8. Database Event Protection
- `crud_vehicle_movement.get_latest_movement_by_plate()` ensures duplicate API calls or frame loops within 120s update the existing active record instead of creating duplicate entry records.

---

## 9. Tests Executed & Verification
- `pytest tests/test_vehicle_detector.py`
- `pytest tests/test_data_engineering_pipeline.py`
- `pytest tests/test_recognition_regression.py`
- `pytest tests/test_tracking_fusion_dedup.py`

### Test Results Summary:
- Total Tests Run: **40**
- Total Tests Passed: **40** (**100% Pass Rate**)
- Total Warnings: **8** (deprecation/torch notices only)
- Total Execution Time: **27.25s**

---

## 10. Performance Measurements
- Single Image Recognition Latency: `~0.12s`
- Video ANPR Processing Speed: `~12.0s` for 245 video frames (`41` sampled frames processed cleanly).

---

## 11. Files Modified
- [`backend/app/ai/config/__init__.py`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/backend/app/ai/config/__init__.py)
- [`backend/app/ai/postprocessing/fusion.py`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/backend/app/ai/postprocessing/fusion.py)
- [`backend/app/ai/vehicle_detector/detector.py`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/backend/app/ai/vehicle_detector/detector.py)
- [`backend/app/ai/postprocessing/plate_validator.py`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/backend/app/ai/postprocessing/plate_validator.py)
- [`backend/app/ai/inference/video_pipeline.py`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/backend/app/ai/inference/video_pipeline.py)
- [`backend/app/services/entry_exit_service.py`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/backend/app/services/entry_exit_service.py)

---

## 12. Files Added
- [`tests/test_tracking_fusion_dedup.py`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/tests/test_tracking_fusion_dedup.py)
- `debug/tracking_validation/tracking_summary.json`
- `debug/tracking_validation/frame_tracking_visualization.jpg`
- `debug/tracking_validation/plate_consensus.json`
- `debug/tracking_validation/event_deduplication.json`
- `docs/TRACKING_MULTIFRAME_DEDUPLICATION_REPORT.md`

---

## 13. Confirmation of Model Weights
- **Model Weights Modified?** **NO.**
- `models/vehicle_detector.pt` and `models/license_plate_detector.pt` were **NOT modified, retrained, or replaced**.
