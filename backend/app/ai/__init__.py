from app.ai.pipeline import ANPRPipeline
from app.ai.config import AI_MODEL_VERSION
from app.ai.models import VehicleDetector, PlateDetector, VehicleTracker
from app.ai.preprocessing import PlateEnhancer, correct_perspective
from app.ai.ocr import OCREngine
from app.ai.postprocessing import IndianPlateValidator, MultiFrameFusion
from app.ai.metrics import PipelineMetrics

__all__ = [
    "ANPRPipeline",
    "AI_MODEL_VERSION",
    "VehicleDetector",
    "PlateDetector",
    "VehicleTracker",
    "PlateEnhancer",
    "correct_perspective",
    "OCREngine",
    "IndianPlateValidator",
    "MultiFrameFusion",
    "PipelineMetrics",
]

pipeline_instance = None


def get_pipeline():
    global pipeline_instance
    if pipeline_instance is None:
        pipeline_instance = ANPRPipeline()
    return pipeline_instance
