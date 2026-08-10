#!/usr/bin/env bash
# ==============================================================================
# Industrial ANPR Trip Management System - NVIDIA Jetson TensorRT Engine Generator
# IMPORTANT: DO NOT RUN THIS SCRIPT ON WINDOWS!
# This script must be executed directly on NVIDIA Jetson hardware running JetPack OS.
# ==============================================================================

set -e

# OS Check - Block Execution on Windows (Git Bash / MSYS / CYGWIN)
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
    echo "======================================================================"
    echo "ERROR: TENSORRT ENGINES CANNOT BE GENERATED ON WINDOWS!"
    echo "======================================================================"
    echo "TensorRT engine files (.engine / .plan) are hardware-specific."
    echo "They MUST be generated on the target NVIDIA Jetson platform."
    echo "Please copy the repository to your Jetson device and run:"
    echo "  bash deployment/generate_engine.sh"
    echo "======================================================================"
    exit 1
fi

echo "======================================================================"
echo "Starting TensorRT Engine Generation on NVIDIA Jetson Hardware..."
echo "======================================================================"

# Determine project directory structure
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
MODELS_DIR="$PROJECT_ROOT/models"

mkdir -p "$MODELS_DIR"

VEHICLE_ONNX="$MODELS_DIR/vehicle_detector.onnx"
VEHICLE_ENGINE="$MODELS_DIR/vehicle_detector.engine"

PLATE_ONNX="$MODELS_DIR/plate_detector.onnx"
PLATE_ENGINE="$MODELS_DIR/plate_detector.engine"

# Verify trtexec utility is available on Jetson
if ! command -v trtexec &> /dev/null; then
    echo "Error: 'trtexec' executable not found in PATH."
    echo "Please ensure NVIDIA TensorRT is installed via JetPack and added to PATH:"
    echo "  export PATH=/usr/src/tensorrt/bin:\$PATH"
    exit 1
fi

# 1. Generate Vehicle Detector TensorRT Engine
echo "----------------------------------------------------------------------"
echo "Building Vehicle Detector TensorRT Engine (FP16 Accelerated)..."
echo "Source ONNX: $VEHICLE_ONNX"
echo "Output Engine: $VEHICLE_ENGINE"
echo "----------------------------------------------------------------------"

if [ ! -f "$VEHICLE_ONNX" ]; then
    echo "Error: Source ONNX model missing at $VEHICLE_ONNX"
    echo "Please run python deployment/export_onnx.py first."
    exit 1
fi

trtexec --onnx="$VEHICLE_ONNX" \
        --saveEngine="$VEHICLE_ENGINE" \
        --fp16 \
        --workspace=2048 \
        --verbose

echo "✓ Vehicle Detector Engine successfully compiled: $VEHICLE_ENGINE"

# 2. Generate Plate Detector TensorRT Engine
echo "----------------------------------------------------------------------"
echo "Building License Plate Detector TensorRT Engine (FP16 Accelerated)..."
echo "Source ONNX: $PLATE_ONNX"
echo "Output Engine: $PLATE_ENGINE"
echo "----------------------------------------------------------------------"

if [ ! -f "$PLATE_ONNX" ]; then
    echo "Error: Source ONNX model missing at $PLATE_ONNX"
    echo "Please run python deployment/export_onnx.py first."
    exit 1
fi

trtexec --onnx="$PLATE_ONNX" \
        --saveEngine="$PLATE_ENGINE" \
        --fp16 \
        --workspace=2048 \
        --verbose

echo "✓ Plate Detector Engine successfully compiled: $PLATE_ENGINE"

echo "======================================================================"
echo "TENSORRT ENGINE COMPILATION COMPLETE!"
echo "Vehicle Engine: $VEHICLE_ENGINE"
echo "Plate Engine:   $PLATE_ENGINE"
echo "======================================================================"
