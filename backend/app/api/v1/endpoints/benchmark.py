from fastapi import APIRouter, Query, BackgroundTasks
from typing import Optional, Dict, Any, List
from pydantic import BaseModel

from app.benchmark.benchmark_runner import BenchmarkRunner
from app.benchmark.system_monitor import SystemMonitor

router = APIRouter(prefix="/system", tags=["Performance & Benchmarking"])

runner = BenchmarkRunner()


class BenchmarkRunRequest(BaseModel):
    source_type: str = "synthetic"  # synthetic | image | video | folder
    source_path: Optional[str] = None
    max_samples: int = 10
    compare_backends: bool = False


@router.get("/benchmark", summary="Get Latest System Benchmark Metrics & Health")
def get_latest_benchmark():
    """Returns the latest system benchmark results, health status, and report output paths."""
    res = runner.run_benchmark(source_type="synthetic", max_samples=5, compare_backends=False)
    return res


@router.get("/performance", summary="Get Real-Time System Performance & Hardware Metrics")
def get_realtime_performance():
    """Returns live real-time CPU, RAM, GPU, Disk, and runtime performance metrics."""
    return SystemMonitor.get_system_snapshot()


@router.post("/benchmark/run", summary="Trigger On-Demand Performance Benchmark Run")
def run_benchmark_on_demand(req: BenchmarkRunRequest):
    """
    Executes a new performance benchmark run across single image, image folder, video file, or synthetic stream.
    Optional comparison mode benchmarks PyTorch vs ONNX vs TensorRT.
    """
    res = runner.run_benchmark(
        source_type=req.source_type,
        source_path=req.source_path,
        max_samples=req.max_samples,
        compare_backends=req.compare_backends,
    )
    return res


@router.get("/benchmark/history", summary="Get Historical Benchmark Log Records")
def get_benchmark_history():
    """Returns historical benchmark execution records."""
    return runner.get_history()
