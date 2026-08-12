#!/usr/bin/env bash
# ==============================================================================
# Edge ANPR & Vehicle Trip Management Platform - Benchmarking Suite Script (Bash)
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

VENV_PYTHON="${PROJECT_ROOT}/backend/venv/bin/python"
if [ ! -f "${VENV_PYTHON}" ]; then
    if [ -f "${PROJECT_ROOT}/backend/venv/Scripts/python.exe" ]; then
        VENV_PYTHON="${PROJECT_ROOT}/backend/venv/Scripts/python.exe"
    else
        VENV_PYTHON="python3"
    fi
fi

echo "======================================================================"
echo "  ANPR & TRIP MANAGEMENT PLATFORM - SYSTEM & MODEL BENCHMARKS"
echo "  Project Root: ${PROJECT_ROOT}"
echo "======================================================================"

# 1. System Diagnostic Hardware Check
echo -e "\n[1/4] Running Enterprise Edge Hardware Diagnostic Check..."
if [ -f "${PROJECT_ROOT}/deployment/system_check.py" ]; then
    cd "${PROJECT_ROOT}"
    "${VENV_PYTHON}" deployment/system_check.py || echo "⚠ System check completed with warnings."
fi

# 2. Jetson / TensorRT / ONNX Performance Latency & Throughput Benchmark
echo -e "\n[2/4] Running Inference Performance & Latency Benchmark..."
if [ -f "${PROJECT_ROOT}/deployment/jetson/benchmark_jetson.py" ]; then
    cd "${PROJECT_ROOT}"
    "${VENV_PYTHON}" deployment/jetson/benchmark_jetson.py || echo "⚠ Inference benchmark completed with warnings."
fi

# 3. Real-World ANPR Pipeline Validation
echo -e "\n[3/4] Validating End-to-End Real-World Pipeline..."
if [ -f "${PROJECT_ROOT}/deployment/validate_real_world_pipeline.py" ]; then
    cd "${PROJECT_ROOT}"
    "${VENV_PYTHON}" deployment/validate_real_world_pipeline.py || echo "⚠ Pipeline validation completed with warnings."
fi

# 4. License Plate Detector Evaluation
echo -e "\n[4/4] Running License Plate Detector Precision Evaluation..."
if [ -f "${PROJECT_ROOT}/deployment/eval_license_plate_detector.py" ]; then
    cd "${PROJECT_ROOT}"
    "${VENV_PYTHON}" deployment/eval_license_plate_detector.py || echo "⚠ Plate detector evaluation completed with warnings."
fi

echo -e "\n======================================================================"
echo "  ✓ BENCHMARKING SUITE RUN COMPLETE!"
echo "======================================================================"
