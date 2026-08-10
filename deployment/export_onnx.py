#!/usr/bin/env python3
"""
Enterprise Edge ONNX Export Utility for Industrial ANPR Trip Management System.
Exports PyTorch YOLO models to ONNX format for high-performance edge deployment.
"""

import os
import sys
import shutil
import logging
from pathlib import Path

# Add backend directory to sys.path to enable imports
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")
logger = logging.getLogger("ONNX_Exporter")


def export_model(model_path: str, output_onnx_path: str, model_name: str) -> bool:
    """Exports a single PyTorch YOLO model to ONNX format."""
    logger.info(f"--- Exporting {model_name} ---")
    logger.info(f"Source PyTorch Weights: {model_path}")
    logger.info(f"Target ONNX File: {output_onnx_path}")

    if not os.path.exists(model_path):
        logger.error(f"PyTorch model file not found at: {model_path}")
        return False

    try:
        from ultralytics import YOLO

        # Load PyTorch model
        model = YOLO(model_path)
        logger.info(f"Loaded PyTorch YOLO model successfully from {model_path}")

        # Ensure target directory exists
        os.makedirs(os.path.dirname(output_onnx_path), exist_ok=True)

        # Perform ONNX export
        # Note: imgsz=640, dynamic=False, opset=12 guarantees broad ONNX Runtime & Jetson compatibility
        exported_file = model.export(format="onnx", imgsz=640, dynamic=False, opset=12, simplify=False)
        logger.info(f"Ultralytics exported raw ONNX file to: {exported_file}")

        # Move/copy exported file to target location if different
        if exported_file and os.path.exists(exported_file):
            if os.path.abspath(exported_file) != os.path.abspath(output_onnx_path):
                shutil.copy2(exported_file, output_onnx_path)
                logger.info(f"Copied exported ONNX file to target: {output_onnx_path}")

        # Verification of exported file
        if os.path.exists(output_onnx_path) and os.path.getsize(output_onnx_path) > 0:
            file_size_mb = os.path.getsize(output_onnx_path) / (1024 * 1024)
            logger.info(f"✓ EXPORT SUCCESS: {model_name} -> {output_onnx_path} ({file_size_mb:.2f} MB)")
            return True
        else:
            logger.error(f"✗ EXPORT FAILED: Output file missing or empty at {output_onnx_path}")
            return False

    except Exception as e:
        logger.error(f"Exception encountered during ONNX export for {model_name}: {e}", exc_info=True)
        return False


def main():
    logger.info("Starting Industrial Vehicle Trip Management System ONNX Export...")

    # Load configuration
    try:
        from app.ai import config
    except ImportError as e:
        logger.error(f"Could not import app.ai.config: {e}")
        sys.exit(1)

    models_dir = Path(config.ROOT_MODELS_DIR)
    models_dir.mkdir(parents=True, exist_ok=True)

    weights_dir = Path(config.MODEL_DIR)
    weights_dir.mkdir(parents=True, exist_ok=True)

    # 1. Vehicle Detector Export
    vehicle_pt_path = config.VEHICLE_DETECTION_MODEL_PT
    vehicle_onnx_target = models_dir / "vehicle_detector.onnx"
    vehicle_success = export_model(vehicle_pt_path, str(vehicle_onnx_target), "Vehicle Detector")

    if vehicle_success:
        # Also copy to backend weights directory for legacy path compatibility
        backend_vehicle_onnx = weights_dir / "vehicle_detector.onnx"
        if str(vehicle_onnx_target) != str(backend_vehicle_onnx):
            shutil.copy2(str(vehicle_onnx_target), str(backend_vehicle_onnx))

    # 2. Plate Detector Export
    plate_pt_path = config.PLATE_DETECTION_MODEL_PT
    plate_onnx_target = models_dir / "plate_detector.onnx"
    plate_success = export_model(plate_pt_path, str(plate_onnx_target), "Plate Detector")

    if plate_success:
        backend_plate_onnx = weights_dir / "plate_detector.onnx"
        if str(plate_onnx_target) != str(backend_plate_onnx):
            shutil.copy2(str(plate_onnx_target), str(backend_plate_onnx))

    # 3. OCR Engine Status
    logger.info("--- OCR Model Info ---")
    logger.info("OCR Engine uses EasyOCR (PyTorch CRAFT detection + Sequence Recognition).")
    logger.info("EasyOCR manages model downloading and internal PyTorch execution dynamically.")

    # Final Summary
    logger.info("=========================================================")
    logger.info("EXPORT SUMMARY")
    logger.info("=========================================================")
    logger.info(f"Vehicle Detector ONNX: {'SUCCESS' if vehicle_success else 'FAILED'}")
    logger.info(f"  Path: {vehicle_onnx_target}")
    logger.info(f"Plate Detector ONNX:   {'SUCCESS' if plate_success else 'FAILED'}")
    logger.info(f"  Path: {plate_onnx_target}")
    logger.info("=========================================================")

    if not (vehicle_success and plate_success):
        sys.exit(1)


if __name__ == "__main__":
    main()
