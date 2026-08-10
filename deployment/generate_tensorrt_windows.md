# TensorRT Generation on Windows vs. NVIDIA Jetson

## Why TensorRT Engines Cannot Be Compiled on Windows for NVIDIA Jetson

TensorRT engine files (`.engine` or `.plan` binaries) contain low-level, machine-code instructions tailored specifically to the host GPU hardware architecture, CUDA compute capability, SM core layout, and TensorRT runtime version.

### Key Reasons Cross-Compilation is Unsupported:
1. **GPU Architecture Mismatch**: A TensorRT engine generated on an x86_64 host with a desktop GPU (e.g. RTX 4070 / GTX 1660) will **NOT** run on an ARM64 NVIDIA Jetson SoC (e.g. Orin Nano, Orin NX, Xavier NX).
2. **OS & Driver Layer**: Jetson runs Linux ARM64 (Ubuntu 20.04/22.04 LTS with JetPack OS) with a unified memory architecture (NVMM), which differs fundamentally from Windows DirectX/WDDM memory drivers.
3. **Hardware Engine Invalidation**: TensorRT validates hardware capabilities during engine deserialization. If an engine file compiled on Windows is transferred to a Jetson device, TensorRT will reject it with a `Deserialization Error: Invalid Engine Header`.

---

## The Correct Production Deployment Workflow

```
┌───────────────────────────┐
│     Windows / Dev PC      │
│  - PyTorch Training       │
│  - Export ONNX Models     │  (python deployment/export_onnx.py)
│  - Verify ONNX Models     │  (python deployment/verify_onnx.py)
└─────────────┬─────────────┘
              │  (Git Push / Copy Codebase)
              ▼
┌───────────────────────────┐
│  NVIDIA Jetson Edge Node  │
│  - Clone Repository       │
│  - Install JetPack & Deps │
│  - Run engine generator:  │  bash deployment/generate_engine.sh
│    ONNX -> .engine        │
└───────────────────────────┘
```

---

## Jetson Quickstart Commands

On your target NVIDIA Jetson device:

```bash
# 1. Clone repository
git clone https://github.com/your-org/ANPR-Trip-Management.git
cd ANPR-Trip-Management

# 2. Run system check
python3 deployment/system_check.py

# 3. Export ONNX (if not already copied)
python3 deployment/export_onnx.py

# 4. Generate TensorRT engines natively on Jetson GPU
bash deployment/generate_engine.sh

# 5. Start Backend Service
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
