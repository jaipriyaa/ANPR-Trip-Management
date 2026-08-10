# NVIDIA Jetson Production Hardware & Software Requirements

This document outlines the official software stack requirements for deploying the Industrial Vehicle Trip Management System on NVIDIA Jetson Edge devices.

---

## Supported Hardware Modules

| Jetson Board Model | Compute Architecture | Tensor Cores | Recommended Max Power Mode |
| :--- | :--- | :--- | :--- |
| **NVIDIA Jetson AGX Orin** | Ampere (64 GB / 32 GB) | 2048 / 1792 CUDA Cores | MAXN (60W) |
| **NVIDIA Jetson Orin NX** | Ampere (16 GB / 8 GB) | 1024 / 512 CUDA Cores | MAXN (25W) |
| **NVIDIA Jetson Orin Nano** | Ampere (8 GB / 4 GB) | 1024 / 512 CUDA Cores | 15W |
| **NVIDIA Jetson Xavier NX** | Volta (16 GB / 8 GB) | 384 CUDA Cores | 20W |

---

## Software Component Matrix

| Software Component | JetPack 5.1.x Target | JetPack 6.0+ Target | Notes |
| :--- | :--- | :--- | :--- |
| **Operating System** | Ubuntu 20.04 LTS (Focal) | Ubuntu 22.04 LTS (Jammy) | Linux for Tegra (L4T) |
| **Linux Kernel** | 5.10.104-tegra | 5.15.136-tegra | Standard L4T Kernel |
| **JetPack OS** | JetPack 5.1.2 / 5.1.3 | JetPack 6.0 EA / GA | Official NVIDIA SDK |
| **CUDA Toolkit** | CUDA 11.4 / 11.8 | CUDA 12.2 / 12.4 | Pre-installed via JetPack |
| **cuDNN** | cuDNN 8.6.0 | cuDNN 8.9.x | Deep Neural Network Library |
| **TensorRT** | TensorRT 8.5.2 | TensorRT 8.6.x / 10.0 | High-performance inference engine |
| **Python Runtime** | Python 3.8 / 3.10 | Python 3.10 / 3.11 | System or Virtual Environment |
| **OpenCV** | 4.5.4 (with GStreamer) | 4.8.0+ (with GStreamer) | Hardware accelerated video decode |
| **ONNX Runtime** | 1.15.1 (GPU / TensorRT) | 1.16.x+ (GPU / TensorRT) | Wheels provided by NVIDIA |

---

## Installing Prerequisites on Jetson

### 1. Update System & Environment
```bash
sudo apt-get update && sudo apt-get install -y \
    build-essential \
    cmake \
    git \
    python3-pip \
    python3-dev \
    libopenblas-dev \
    libopenmpi-dev
```

### 2. Export Environment Paths (`~/.bashrc`)
```bash
export PATH=/usr/local/cuda/bin:/usr/src/tensorrt/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH
```

### 3. Verify NVIDIA CUDA & TensorRT Tools
```bash
nvcc --version
trtexec --help
```
