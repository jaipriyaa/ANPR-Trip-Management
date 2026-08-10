import os
import sys
import pytest
from ultralytics import YOLO

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PT = os.path.join(PROJECT_ROOT, "models", "license_plate_detector.pt")
MODEL_ONNX = os.path.join(PROJECT_ROOT, "models", "license_plate_detector.onnx")


def test_license_plate_model_files_exist():
    """Verify production PyTorch and ONNX plate detector model files exist."""
    assert os.path.exists(MODEL_PT), f"PyTorch plate model missing: {MODEL_PT}"
    assert os.path.exists(MODEL_ONNX), f"ONNX plate model missing: {MODEL_ONNX}"


def test_license_plate_model_single_class():
    """Verify license plate detector has exactly 1 class: 'license_plate'."""
    model = YOLO(MODEL_PT)
    assert len(model.names) == 1, f"Expected 1 class, got {len(model.names)}"
    assert model.names[0] == "license_plate", f"Expected class 'license_plate', got {model.names[0]}"


def test_license_plate_onnx_tensor_shape():
    """Verify ONNX plate detector has output shape [1, 5, 8400] (5 channels = 4 bbox + 1 class)."""
    import onnxruntime as ort
    session = ort.InferenceSession(MODEL_ONNX, providers=["CPUExecutionProvider"])
    outputs = session.get_outputs()
    out_shape = outputs[0].shape
    assert len(out_shape) == 3, f"Unexpected ONNX output shape: {out_shape}"
    assert out_shape[1] == 5, f"Expected 5 output channels (4 bbox + 1 class), got {out_shape[1]}"
