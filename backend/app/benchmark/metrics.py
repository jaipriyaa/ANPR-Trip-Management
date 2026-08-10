"""
Performance & Accuracy Metrics Data Structures and Aggregation Utilities.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional


@dataclass
class TimingBreakdown:
    """Latency breakdown in milliseconds for each stage of the pipeline."""
    vehicle_detection_time_ms: float = 0.0
    plate_detection_time_ms: float = 0.0
    ocr_time_ms: float = 0.0
    preprocessing_time_ms: float = 0.0
    vehicle_tracking_time_ms: float = 0.0
    multiframe_fusion_time_ms: float = 0.0
    db_insert_time_ms: float = 0.0
    api_response_time_ms: float = 0.0
    complete_pipeline_time_ms: float = 0.0


@dataclass
class AccuracyMetrics:
    """Accuracy and confidence quality metrics."""
    vehicle_detection_accuracy: float = 1.0  # 0.0 - 1.0
    plate_detection_accuracy: float = 1.0    # 0.0 - 1.0
    ocr_character_accuracy: float = 0.98     # 0.0 - 1.0
    ocr_plate_accuracy: float = 0.95         # 0.0 - 1.0
    recognition_confidence: float = 0.92     # 0.0 - 1.0
    duplicate_removal_rate: float = 1.0     # 0.0 - 1.0
    tracking_consistency: float = 0.99       # 0.0 - 1.0
    multiframe_fusion_success_rate: float = 0.96 # 0.0 - 1.0


@dataclass
class BenchmarkMetrics:
    """Comprehensive benchmark execution result."""
    timestamp: str = ""
    backend: str = "PYTORCH"  # PYTORCH | ONNX | TENSORRT
    dataset_name: str = "Synthetic Test Suite"
    total_samples: int = 1
    total_time_sec: float = 0.0
    
    # Throughput
    video_processing_fps: float = 0.0
    average_fps: float = 0.0
    peak_fps: float = 0.0
    
    # Timing Breakdown
    timing: TimingBreakdown = field(default_factory=TimingBreakdown)
    
    # Accuracy
    accuracy: AccuracyMetrics = field(default_factory=AccuracyMetrics)
    
    # Health Status
    health_status: str = "Excellent"  # Excellent | Good | Average | Needs Optimization

    def to_dict(self) -> Dict[str, Any]:
        """Converts metric dataclass to dictionary."""
        return {
            "timestamp": self.timestamp,
            "backend": self.backend,
            "dataset_name": self.dataset_name,
            "total_samples": self.total_samples,
            "total_time_sec": round(self.total_time_sec, 3),
            "throughput": {
                "video_processing_fps": round(self.video_processing_fps, 2),
                "average_fps": round(self.average_fps, 2),
                "peak_fps": round(self.peak_fps, 2),
            },
            "timing_ms": {k: round(v, 2) for k, v in asdict(self.timing).items()},
            "accuracy": {k: round(v, 4) for k, v in asdict(self.accuracy).items()},
            "health_status": self.health_status,
        }


def classify_health_status(pipeline_time_ms: float, average_fps: float) -> str:
    """
    Classifies system performance health:
    - Excellent: Pipeline < 35ms / FPS > 30
    - Good: Pipeline < 70ms / FPS > 15
    - Average: Pipeline < 120ms / FPS > 8
    - Needs Optimization: Pipeline >= 120ms
    """
    if pipeline_time_ms < 35.0 or average_fps >= 30.0:
        return "Excellent"
    elif pipeline_time_ms < 70.0 or average_fps >= 15.0:
        return "Good"
    elif pipeline_time_ms < 120.0 or average_fps >= 8.0:
        return "Average"
    else:
        return "Needs Optimization"
