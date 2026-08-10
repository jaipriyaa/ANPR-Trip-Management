#!/usr/bin/env bash
# NVIDIA Jetson Deployment & Environment Setup Script

set -e

echo "============================================================"
echo "    NVIDIA JETSON EDGE DEPLOYMENT SETUP"
echo "============================================================"

# Check if running on Jetson
if [ -f /etc/nv_tegra_release ]; then
    echo "[INFO] Detected NVIDIA Tegra/Jetson platform:"
    cat /etc/nv_tegra_release
else
    echo "[WARNING] Not running on NVIDIA Jetson hardware. Proceeding with general CUDA/CPU setup."
fi

# Set MAX performance mode on Jetson if available
if command -v nvpmodel &> /dev/null; then
    echo "[INFO] Setting Jetson power mode to MAX performance..."
    sudo nvpmodel -m 0 || true
fi

if command -v jetson_clocks &> /dev/null; then
    echo "[INFO] Locking Jetson clocks for benchmark consistency..."
    sudo jetson_clocks || true
fi

# Install dependencies
echo "[INFO] Installing Python dependencies for Jetson..."
pip3 install -r requirements-jetson.txt

echo "[SUCCESS] Environment setup complete."
