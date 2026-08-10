import pytest
from app.ai.inference.video_pipeline import VideoANPRPipeline, estimate_direction


def test_multiframe_ocr_fusion_character_voting():
    pipeline = VideoANPRPipeline()

    # Simulate multi-frame OCR observations for a single tracklet
    observations = [
        {
            "frame_idx": 10,
            "timestamp": 1.0,
            "raw_text": "MH14TCF200F",
            "plate_text": "MH14TCF200F",
            "ocr_confidence": 0.85,
            "is_valid_plate": True,
        },
        {
            "frame_idx": 15,
            "timestamp": 1.5,
            "raw_text": "MH14TCF20OF",  # 'O' instead of '0'
            "plate_text": "MH14TCF200F", # Corrected by validator
            "ocr_confidence": 0.70,
            "is_valid_plate": True,
        },
        {
            "frame_idx": 20,
            "timestamp": 2.0,
            "raw_text": "MH14TCF200F",
            "plate_text": "MH14TCF200F",
            "ocr_confidence": 0.94,
            "is_valid_plate": True,
        },
        {
            "frame_idx": 25,
            "timestamp": 2.5,
            "raw_text": "MH14TCF200F",
            "plate_text": "MH14TCF200F",
            "ocr_confidence": 0.97,
            "is_valid_plate": True,
        },
    ]

    fused_result = pipeline.fuse_multiframe_ocr(observations)

    assert fused_result["plate_text"] == "MH14TCF200F"
    assert fused_result["corrected_plate"] == "MH14TCF200F"
    assert fused_result["is_valid_plate"] is True
    assert fused_result["confidence"] == 0.97
    assert len(fused_result["per_frame_history"]) == 4


def test_direction_estimation():
    # Moving downwards (cy increasing: entering)
    entering_bboxes = [
        [100, 100, 300, 300], # cy = 200
        [100, 200, 300, 400], # cy = 300
        [100, 300, 300, 500], # cy = 400
    ]
    assert estimate_direction(entering_bboxes) == "Entering"

    # Moving upwards (cy decreasing: exiting)
    exiting_bboxes = [
        [100, 400, 300, 600], # cy = 500
        [100, 250, 300, 450], # cy = 350
        [100, 100, 300, 300], # cy = 200
    ]
    assert estimate_direction(exiting_bboxes) == "Exiting"
