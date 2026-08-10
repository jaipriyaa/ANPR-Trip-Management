# TRIP STATE ENGINE, ENTRY/EXIT MATCHING & DWELL TIME REPORT (TARGET 2)

##  EXECUTIVE SUMMARY

Target 2 has been fully implemented, integrated, and verified on the live production ANPR system. The implementation enhances the existing `TripEngine` in `backend/app/services/trip_service.py` to enforce a strict state machine, automated entry/exit matching, dwell-time calculation, late-arrival metrics, overstay alerts, state history tracking, and exception handling.

All 61 test cases across 5 test suites (including 40 Target 1 tests and 21 Target 2 tests) pass with **100% success rate**. All AI model weights (`models/vehicle_detector.pt` and `models/license_plate_detector.pt`) remained untouched.

---

## 1. EXISTING TRIP ARCHITECTURE & CHANGES MADE

- **Reused Existing Models & Services**: Retained database models (`ScheduledTrip`, `TripStatusHistory`, `VehicleMovement`, `Vehicle`) and services (`TripEngine`, `EntryExitEngine`, `AuthorizationService`). No duplicate tables or services were created.
- **Strict State Machine Integration**: Added `VALID_TRANSITIONS` graph and `transition_state()` validator to prevent invalid or out-of-order state jumps.
- **Automatic History Logging**: Every state change invokes `crud_scheduled_trip.record_status_change()` to append an immutable record to `trip_status_history`.
- **Dwell Time & Metrics**: Implemented non-negative dwell time calculation (`calculate_dwell_time`), late arrival detection (`calculate_late_arrival`), and overstay warning system (`check_overstay`).

---

## 2. TRIP STATE MACHINE & TRANSITIONS

The system supports 9 explicit states:

```
                  ┌──────────────┐
                  │  SCHEDULED   │
                  └──────┬───────┘
                         │ (Gate Arrival)
                  ┌──────▼───────┐
                  │   ARRIVED    │
                  └──────┬───────┘
                         │ (Gate Authorization Approved)
                  ┌──────▼───────┐
                  │ENTRY_APPROVED│
                  └──────┬───────┘
                         │ (Entry Barrier Pass)
                  ┌──────▼───────┐
                  │ INSIDE_PLANT │
                  └──────┬───────┘
                         │ (Destination Checkpoint)
                  ┌──────▼───────┐
                  │AT_DESTINATION│
                  └──────┬───────┘
                         │ (Exit Gate ANPR Motion)
                  ┌──────▼───────┐
                  │ EXIT_DETECTED│
                  └──────┬───────┘
                         │ (Exit Barrier Pass / Dwell Calculation)
                  ┌──────▼───────┐
                  │  COMPLETED   │
                  └──────────────┘

Alternative Flows:
  - SCHEDULED -> CANCELLED
  - Any Unexpected Condition -> EXCEPTION
```

### Transition Validation Matrix

| From State | Allowed Target States |
| :--- | :--- |
| `SCHEDULED` | `ARRIVED`, `ENTRY_APPROVED`, `INSIDE_PLANT`, `CANCELLED`, `EXCEPTION` |
| `ARRIVED` | `ENTRY_APPROVED`, `INSIDE_PLANT`, `CANCELLED`, `EXCEPTION` |
| `ENTRY_APPROVED` | `INSIDE_PLANT`, `CANCELLED`, `EXCEPTION` |
| `INSIDE_PLANT` | `AT_DESTINATION`, `EXIT_DETECTED`, `COMPLETED`, `EXCEPTION` |
| `AT_DESTINATION` | `EXIT_DETECTED`, `COMPLETED`, `EXCEPTION` |
| `EXIT_DETECTED` | `COMPLETED`, `EXCEPTION` |
| `COMPLETED` | *None (Terminal)* |
| `CANCELLED` | *None (Terminal)* |
| `EXCEPTION` | `INSIDE_PLANT`, `COMPLETED`, `CANCELLED` |

*Attempting an invalid transition (e.g. `COMPLETED` -> `INSIDE_PLANT`) raises an `HTTPException(400)`.*

---

## 3. ENTRY & EXIT MATCHING LOGIC

1. **Entry Matching**:
   - Vehicle plate recognized at entry gate.
   - Searches active scheduled trips for matching vehicle ID or plate.
   - If found: Transitions state `SCHEDULED` -> `ARRIVED` -> `ENTRY_APPROVED` -> `INSIDE_PLANT`. Evaluates arrival delay (`ON_TIME` vs `LATE`).
   - If not found: Auto-creates ad-hoc trip for master vehicle or flags for `MANUAL_REVIEW`.

2. **Exit Matching**:
   - Vehicle plate recognized at exit gate (`direction="Exiting"`).
   - Searches active trip for vehicle in states `INSIDE`, `INSIDE_PLANT`, `AT_DESTINATION`, or `EXIT_DETECTED`.
   - Matches exit event to the SAME active trip record.
   - Transitions state to `EXIT_DETECTED` -> `COMPLETED`.
   - Calculates exact dwell time and checks for overstay condition.

3. **Duplicate Exit Suppression**:
   - Reuses Target 1 120-second deduplication. If a vehicle exits and multiple frames trigger within 120s, the system suppresses duplicate trip creation and returns the existing completed trip.

---

## 4. METRICS & COMPUTATIONS

- **Dwell Time**:
  $$\text{dwell\_seconds} = \max(0, \text{exit\_time} - \text{entry\_time})$$
  Format: `"X Hours, Y Minutes, Z Seconds"`
- **Late Arrival**:
  $$\text{delay\_seconds} = \text{actual\_entry} - \text{expected\_entry}$$
  If $\text{delay\_seconds} > 900\text{s}$ ($15\text{ mins}$): Status = `LATE`. Else Status = `ON_TIME`.
- **Overstay Detection**:
  $$\text{allowed\_seconds} = \text{expected\_exit} - \text{expected\_entry}$$
  If $\text{dwell\_seconds} > \text{allowed\_seconds}$: `is_overstay = True`, alert generated.

---

## 5. DEBUG ARTIFACTS (`debug/trip_validation/`)

| File Name | Description |
| :--- | :--- |
| [`trip_state_history.json`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/debug/trip_validation/trip_state_history.json) | Complete chronological timeline of state transitions for `TRIP-2026-144`. |
| [`entry_exit_matching.json`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/debug/trip_validation/entry_exit_matching.json) | Measured entry and exit matching verification data. |
| [`dwell_time_calculation.json`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/debug/trip_validation/dwell_time_calculation.json) | Dwell time calculation results in seconds, minutes, and formatted string. |
| [`late_arrival.json`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/debug/trip_validation/late_arrival.json) | Arrival delay calculation and status (`LATE` vs `ON_TIME`). |
| [`overstay_detection.json`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/debug/trip_validation/overstay_detection.json) | Overstay check results and excess stay duration. |
| [`end_to_end_trip.json`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/debug/trip_validation/end_to_end_trip.json) | Summary of real-world end-to-end trip verification. |

---

## 6. VERIFICATION RESULTS

### PyTest Suite Breakdown
- `tests/test_vehicle_detector.py`: **11/11 PASSED**
- `tests/test_data_engineering_pipeline.py`: **5/5 PASSED**
- `tests/test_recognition_regression.py`: **16/16 PASSED**
- `tests/test_tracking_fusion_dedup.py`: **8/8 PASSED**
- `tests/test_trip_state_machine.py`: **21/21 PASSED**
- **Total Suite Result:** **61/61 PASSED (100% Pass Rate)**

---

## 7. FILES MODIFIED & ADDED

### Files Modified:
- [`backend/app/services/trip_service.py`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/backend/app/services/trip_service.py): Enhanced `TripEngine` with state machine, state history, entry/exit matching, dwell time, late arrival, and overstay calculation.
- [`backend/app/crud/crud_scheduled_trip.py`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/backend/app/crud/crud_scheduled_trip.py): Updated active trip state filters to support all Target 2 states.
- [`backend/app/services/vehicle_recognition_service.py`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/backend/app/services/vehicle_recognition_service.py): Passed direction parameter to `process_ai_recognition_event()`.

### Files Added:
- [`tests/test_trip_state_machine.py`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/tests/test_trip_state_machine.py): 21 comprehensive mandatory unit tests.
- [`scratch/verify_target2_e2e.py`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/scratch/verify_target2_e2e.py): Real end-to-end verification script.
- [`docs/TRIP_STATE_ENTRY_EXIT_REPORT.md`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/docs/TRIP_STATE_ENTRY_EXIT_REPORT.md): This report artifact.

---

## 8. CONFIRMATION OF MODEL WEIGHT INTEGRITY

- `models/vehicle_detector.pt`: **UNTOUCHED / UNCHANGED**
- `models/license_plate_detector.pt`: **UNTOUCHED / UNCHANGED**
- OCR Models: **UNTOUCHED / UNCHANGED**

---

TARGET 2 VERIFICATION

Tests: 61/61 PASSED
State machine: PASS
Entry matching: PASS
Exit matching: PASS
Dwell time calculation: PASS
Late arrival detection: PASS
Overstay detection: PASS
Duplicate exit suppression: PASS
State history recorded: PASS
Image regression: PASS
Video regression: PASS
Model weights modified: NO

FINAL VERDICT:
COMPLETE
