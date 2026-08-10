#!/usr/bin/env bash
# TensorRT Engine Build Script for ONNX Models

set -e

echo "============================================================"
echo "    BUILDING TENSORRT FP16 ENGINES FOR JETSON"
echo "============================================================"

MODELS_DIR="../../models"
TRT_OUT_DIR="../../models/tensorrt"
mkdir -p "$TRT_OUT_DIR"

TRTEXEC=$(command -v trtexec || echo "")

if [ -z "$TRTEXEC" ]; then
    echo "[ERROR] 'trtexec' executable not found in PATH. Ensure CUDA & TensorRT are installed."
    echo "[INFO] If TensorRT is unavailable, ANPR backend will automatically fall back to ONNX or PyTorch."
    exit 1
fi

echo "[1/2] Converting vehicle_detector.onnx -> vehicle_detector_fp16.engine..."
"$TRTEXEC" \
    --onnx="$MODELS_DIR/vehicle_detector.onnx" \
    --saveEngine="$TRT_OUT_DIR/vehicle_detector_fp16.engine" \
    --fp16 \
    --workspace=2048

echo "[2/2] Converting license_plate_detector.onnx -> license_plate_detector_fp16.engine..."
"$TRTEXEC" \
    --onnx="$MODELS_DIR/license_plate_detector.onnx" \
    --saveEngine="$TRT_OUT_DIR/license_plate_detector_fp16.engine" \
    --fp16 \
    --workspace=2048

echo "[SUCCESS] TensorRT engines created successfully in $TRT_OUT_DIR."
