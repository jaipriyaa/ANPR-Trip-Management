import logging
from collections import Counter, defaultdict
from typing import List, Optional, Tuple

from app.ai import config

logger = logging.getLogger(__name__)


class MultiFrameFusion:
    def __init__(self):
        self.min_frames = config.FUSION_MIN_FRAMES
        self.min_confidence = config.FUSION_MIN_CONFIDENCE
        self.weight_confidence = config.FUSION_WEIGHT_CONFIDENCE
        self.weight_frequency = config.FUSION_WEIGHT_FREQUENCY

    def fuse(self, frame_results: List[dict]) -> dict:
        if not frame_results:
            return {
                "plate_text": "",
                "confidence": 0.0,
                "raw_text": "",
                "is_valid": False,
                "fusion_method": "empty",
                "frame_count": 0,
                "fused_frames": 0,
            }

        valid = [r for r in frame_results if r.get("plate_text") and len(r["plate_text"]) >= 4]

        if not valid:
            best = max(frame_results, key=lambda r: r.get("confidence", 0.0))
            return {
                "plate_text": best.get("plate_text", ""),
                "confidence": round(float(best.get("confidence", 0.0)), 4),
                "raw_text": best.get("raw_text", ""),
                "is_valid": False,
                "fusion_method": "single_best_unverified",
                "frame_count": len(frame_results),
                "fused_frames": 0,
            }

        if len(valid) == 1:
            best = valid[0]
            return {
                "plate_text": best["plate_text"],
                "confidence": round(float(best.get("ocr_confidence", best.get("confidence", 0.0))), 4),
                "raw_text": best.get("raw_text", best["plate_text"]),
                "is_valid": bool(best.get("is_valid_plate", True)),
                "fusion_method": "single_frame",
                "frame_count": len(frame_results),
                "fused_frames": 1,
            }

        # Multi-factor score fusion across candidates
        candidate_obs = defaultdict(list)
        for r in valid:
            candidate_obs[r["plate_text"]].append(r)

        total_valid = len(valid)
        scored_candidates = []

        for text, obs_list in candidate_obs.items():
            freq = len(obs_list)
            rep_ratio = freq / float(total_valid)
            ocr_conf = max(float(o.get("ocr_confidence", o.get("confidence", 0.5))) for o in obs_list)
            det_conf = max(float(o.get("confidence", 0.5)) for o in obs_list)
            is_valid = any(bool(o.get("is_valid_plate", False)) for o in obs_list)
            val_score = 1.0 if is_valid else 0.2

            # Candidate Score Formula: OCR(35%) + PlateDet(25%) + Repetition(20%) + Validation(20%)
            score = (ocr_conf * 0.35) + (det_conf * 0.25) + (rep_ratio * 0.20) + (val_score * 0.20)
            scored_candidates.append({
                "plate_text": text,
                "score": score,
                "ocr_confidence": ocr_conf,
                "det_confidence": det_conf,
                "frequency": freq,
                "is_valid": is_valid,
                "raw_text": obs_list[0].get("raw_text", text),
            })

        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        winner = scored_candidates[0]

        char_consistency = self._check_character_consistency(valid)
        final_conf = min(1.0, winner["score"] + (0.05 if char_consistency > 0.85 else 0.0))

        return {
            "plate_text": winner["plate_text"],
            "confidence": round(final_conf, 4),
            "raw_text": winner["raw_text"],
            "is_valid": winner["is_valid"],
            "fusion_method": "Weighted Character-Level Majority Voting & Format Rules",
            "frame_count": len(frame_results),
            "fused_frames": len(valid),
            "consensus_count": winner["frequency"],
            "character_consistency": round(char_consistency, 4),
        }

    def _check_character_consistency(self, valid_results: list) -> float:
        if len(valid_results) < 2:
            return 1.0

        texts = [r["plate_text"] for r in valid_results if r.get("plate_text")]
        if not texts:
            return 1.0

        min_len = min(len(t) for t in texts)
        if min_len < 4:
            return 1.0

        consistent_chars = 0
        total_positions = min_len * len(texts)

        for pos in range(min_len):
            chars_at_pos = [t[pos] if pos < len(t) else "" for t in texts]
            most_common = Counter(chars_at_pos).most_common(1)[0]
            consistent_chars += most_common[1]

        return consistent_chars / max(total_positions, 1)
