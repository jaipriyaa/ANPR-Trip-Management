from fastapi import APIRouter
from app.ai.inference.backend_selector import get_active_backend_info

router = APIRouter(prefix="/system", tags=["System Diagnostics & Hardware"])


@router.get("/health", summary="System & AI Inference Hardware Health Check")
def get_system_health():
    """
    Returns system status, active backend (TensorRT | ONNX | PyTorch),
    CUDA availability, GPU device details, and AI model version.
    """
    return get_active_backend_info()
