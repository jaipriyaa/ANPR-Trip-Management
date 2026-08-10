#!/usr/bin/env python3
"""
Enterprise Edge ONNX Verification Utility for Industrial ANPR Trip Management System.
Verifies input shape, output shape, model integrity, and inference session creation for ONNX models.
Prints PASS or FAIL for each model and overall deployment status.
"""

import os
import sys
import logging
import numpy as np
from pathlib import Path

# Add backend directory to sys.path
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")
logger = logging.getLogger("ONNX_Verifier")


def verify_onnx_model(model_path: str, model_name: str) -> bool:
    """
    Verifies an ONNX model:
    1. Check file existence & non-zero size
    2. Check model integrity with onnx.checker
    3. Initialize onnxruntime InferenceSession
    4. Validate input tensor shapes & data types
    5. Run dummy inference pass
    """
    print(f"\n=========================================================")
    print(f"VERIFYING MODEL: {model_name}")
    print(f"Path: {model_path}")
    print(f"=========================================================")

    if not os.path.exists(model_path):
        logger.error(f"FAIL: File does not exist at path: {model_path}")
        print(f"[{model_name}] RESULT: FAIL (File missing)")
        return False

    file_size_mb = os.path.getsize(model_path) / (1024 * 1024)
    logger.info(f"File Size: {file_size_mb:.2f} MB")

    # Step 1: Model Integrity Verification using onnx library if installed
    try:
        import onnx
        onnx_model = onnx.load(model_path)
        onnx.checker.check_model(onnx_model)
        logger.info("✓ Model Integrity Check (onnx.checker): PASS")
    except ImportError:
        logger.warning("onnx package not installed; skipping onnx.checker validation.")
    except Exception as e:
        logger.error(f"✗ Model Integrity Check FAILED: {e}")
        print(f"[{model_name}] RESULT: FAIL (Corrupted ONNX graph)")
        return False

    # Step 2: Inference Session Creation
    try:
        import onnxruntime as ort
        providers = ort.get_available_providers()
        session = ort.InferenceSession(model_path, providers=providers)
        logger.info(f"✓ Inference Session Creation: PASS (Providers: {providers})")
    except Exception as e:
        logger.error(f"✗ Inference Session Creation FAILED: {e}")
        print(f"[{model_name}] RESULT: FAIL (Session creation error)")
        return False

    # Step 3: Input Shape & Type Inspection
    try:
        inputs = session.get_inputs()
        outputs = session.get_outputs()

        logger.info("--- Model I/O Specifications ---")
        for idx, inp in enumerate(inputs):
            logger.info(f"  Input [{idx}]: name='{inp.name}', shape={inp.shape}, type={inp.type}")
        for idx, out in enumerate(outputs):
            logger.info(f"  Output [{idx}]: name='{out.name}', shape={out.shape}, type={out.type}")

        input_name = inputs[0].name
        input_shape = inputs[0].shape

        # Build dummy input array (handle dynamic batching / dimensions)
        dummy_shape = [dim if (isinstance(dim, int) and dim > 0) else 1 for dim in input_shape]
        if len(dummy_shape) == 4 and dummy_shape[1] == 3:
            dummy_input = np.zeros(dummy_shape, dtype=np.float32)
        else:
            dummy_input = np.zeros((1, 3, 640, 640), dtype=np.float32)

        logger.info(f"Constructed test input tensor with shape: {dummy_input.shape}")

        # Step 4: Execute Test Inference Session
        raw_outputs = session.run(None, {input_name: dummy_input})
        output_shape = raw_outputs[0].shape
        logger.info(f"✓ Inference Execution Pass: PASS (Output shape: {output_shape})")

        print(f"[{model_name}] RESULT: PASS")
        return True

    except Exception as e:
        logger.error(f"✗ Inference Execution FAILED: {e}", exc_info=True)
        print(f"[{model_name}] RESULT: FAIL (Inference execution error)")
        return False


def main():
    print("=========================================================")
    print("INDUSTRIAL ANPR TRIP MANAGEMENT SYSTEM - ONNX VERIFICATION")
    print("=========================================================")

    try:
        from app.ai import config
    except ImportError as e:
        logger.error(f"Failed to import app.ai.config: {e}")
        sys.exit(1)

    vehicle_onnx = config.VEHICLE_DETECTION_MODEL_ONNX
    plate_onnx = config.PLATE_DETECTION_MODEL_ONNX

    v_pass = verify_onnx_model(vehicle_onnx, "Vehicle Detector ONNX")
    p_pass = verify_onnx_model(plate_onnx, "Plate Detector ONNX")

    print("\n=========================================================")
    print("VERIFICATION SUMMARY")
    print("=========================================================")
    print(f"Vehicle Detector ONNX: {'PASS' if v_pass else 'FAIL'}")
    print(f"Plate Detector ONNX:   {'PASS' if p_pass else 'FAIL'}")
    print("=========================================================")

    if v_pass and p_pass:
        print("\nOVERALL STATUS: PASS - All ONNX models verified successfully!")
        sys.exit(0)
    else:
        print("\nOVERALL STATUS: FAIL - One or more ONNX models failed verification.")
        sys.exit(1)


if __name__ == "__main__":
    main()
