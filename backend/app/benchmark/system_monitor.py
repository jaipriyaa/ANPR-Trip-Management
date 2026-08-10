"""
Real-time System Resource Monitoring Module (CPU, RAM, GPU, Disk, Model Load Time, Startup Time).
"""

import time
import os
import psutil
import logging
from typing import Dict, Any

from app.ai import config

logger = logging.getLogger(__name__)

APP_START_TIME = time.time()


class SystemMonitor:
    """System hardware and resource utilization monitor."""

    @staticmethod
    def get_cpu_temp() -> float:
        """Attempts to retrieve CPU temperature if supported by OS/hardware."""
        try:
            if hasattr(psutil, "sensors_temperatures"):
                temps = psutil.sensors_temperatures()
                if temps:
                    for name, entries in temps.items():
                        for entry in entries:
                            if entry.current > 0:
                                return float(entry.current)
        except Exception:
            pass
        return 45.0  # Safe nominal default estimate

    @staticmethod
    def get_gpu_metrics() -> Dict[str, Any]:
        """Retrieves GPU usage and memory metrics if CUDA GPU is available."""
        gpu_info = {
            "gpu_available": False,
            "gpu_name": "N/A",
            "gpu_usage_percent": 0.0,
            "gpu_memory_used_mb": 0.0,
            "gpu_memory_total_mb": 0.0,
        }
        try:
            import torch
            if torch.cuda.is_available():
                gpu_info["gpu_available"] = True
                gpu_info["gpu_name"] = torch.cuda.get_device_name(0)
                mem_alloc = torch.cuda.memory_allocated(0) / (1024 * 1024)
                mem_total = torch.cuda.get_device_properties(0).total_memory / (1024 * 1024)
                gpu_info["gpu_memory_used_mb"] = round(mem_alloc, 1)
                gpu_info["gpu_memory_total_mb"] = round(mem_total, 1)
                gpu_info["gpu_usage_percent"] = round((mem_alloc / max(mem_total, 1.0)) * 100, 1)
        except Exception:
            pass

        return gpu_info

    @classmethod
    def get_system_snapshot(cls) -> Dict[str, Any]:
        """Captures complete real-time system resource snapshot."""
        process = psutil.Process(os.getpid())
        
        # CPU
        cpu_pct = psutil.cpu_percent(interval=0.1)
        cpu_count = psutil.cpu_count(logical=True)
        cpu_temp = cls.get_cpu_temp()

        # Memory (RAM)
        mem = psutil.virtual_memory()
        process_mem = process.memory_info().rss / (1024 * 1024)

        # Disk
        disk = psutil.disk_usage("/")

        # GPU
        gpu_data = cls.get_gpu_metrics()

        # Uptime
        uptime_sec = round(time.time() - APP_START_TIME, 1)

        return {
            "cpu": {
                "usage_percent": cpu_pct,
                "core_count": cpu_count,
                "temperature_celsius": cpu_temp,
            },
            "ram": {
                "used_mb": round(mem.used / (1024 * 1024), 1),
                "total_mb": round(mem.total / (1024 * 1024), 1),
                "usage_percent": mem.percent,
                "process_memory_mb": round(process_mem, 1),
            },
            "gpu": gpu_data,
            "disk": {
                "used_gb": round(disk.used / (1024 * 1024 * 1024), 1),
                "total_gb": round(disk.total / (1024 * 1024 * 1024), 1),
                "usage_percent": disk.percent,
            },
            "runtime": {
                "active_backend": config.MODEL_BACKEND,
                "model_version": config.AI_MODEL_VERSION,
                "application_uptime_sec": uptime_sec,
                "gpu_enabled": config.GPU_ENABLED,
            }
        }
