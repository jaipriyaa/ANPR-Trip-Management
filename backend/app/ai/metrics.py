import time
import logging
from dataclasses import dataclass, field
from typing import Dict

logger = logging.getLogger(__name__)


@dataclass
class StageMetrics:
    stage_name: str
    success: bool = False
    duration_ms: float = 0.0
    items_found: int = 0
    confidence: float = 0.0
    details: dict = field(default_factory=dict)


class PipelineMetrics:
    def __init__(self):
        self.stages: Dict[str, StageMetrics] = {}
        self._timers: Dict[str, float] = {}

    def start(self, stage: str):
        self._timers[stage] = time.time()
        self.stages[stage] = StageMetrics(stage_name=stage)

    def end(self, stage: str, success: bool = True, items: int = 0, confidence: float = 0.0, details: dict = None):
        elapsed = (time.time() - self._timers.pop(stage, time.time())) * 1000
        if stage in self.stages:
            self.stages[stage].success = success
            self.stages[stage].duration_ms = elapsed
            self.stages[stage].items_found = items
            self.stages[stage].confidence = confidence
            self.stages[stage].details = details or {}

    def total_time(self) -> float:
        return sum(s.duration_ms for s in self.stages.values())

    def to_dict(self) -> dict:
        return {
            name: {
                "success": s.success,
                "duration_ms": round(s.duration_ms, 1),
                "items_found": s.items_found,
                "confidence": round(s.confidence, 4),
                "details": s.details,
            }
            for name, s in self.stages.items()
        }
