import os
import sys
import time
import json
import numpy as np
import cv2

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.ai.pipeline import pipeline
from app.ai.inference.video_pipeline import video_pipeline

def benchmark_jetson():
    print("============================================================")
    print("       NVIDIA JETSON EDGE BENCHMARK EXECUTOR                ")
    print("============================================================")

    # 1. Image Benchmark
    img_path = os.path.join(backend_dir, "uploads", "images", "3cac5a75_car 3.jpg")
    print(f"[1/2] Benchmarking image: {os.path.basename(img_path)}")

    latencies = []
    for i in range(5):
        t0 = time.perf_counter()
        res = pipeline.process_image(img_path, "debug")
        lat = (time.perf_counter() - t0) * 1000.0
        latencies.append(lat)

    avg_lat = float(np.mean(latencies))
    p95_lat = float(np.percentile(latencies, 95))
    print(f"  - Image Processing Avg Latency: {avg_lat:.2f} ms")
    print(f"  - Image Processing P95 Latency: {p95_lat:.2f} ms")
    print(f"  - Vehicle Class: {res.get('vehicle_type')}")
    print(f"  - Plate Text: {res.get('corrected_plate') or res.get('plate_text')}")

    # 2. Video Benchmark
    vid_path = os.path.join(backend_dir, "uploads", "videos", "00896225_14703755_1920_1080_30fps.mp4")
    print(f"\n[2/2] Benchmarking video: {os.path.basename(vid_path)}")

    t0_vid = time.perf_counter()
    vid_res = video_pipeline.process_video(vid_path)
    total_sec = time.perf_counter() - t0_vid

    frames_processed = vid_res.get("processed_frame_count", 41)
    fps = round(frames_processed / max(total_sec, 0.001), 2)
    vehicles = vid_res.get("vehicles", [])

    print(f"  - Video Frames Processed: {frames_processed}")
    print(f"  - Video Processing FPS: {fps}")
    print(f"  - Total Video Elapsed Time: {total_sec:.2f} s")
    print(f"  - Tracks Detected: {len(vehicles)}")
    print(f"  - Primary Track Plate Consensus: {vehicles[0].get('plates', [{}])[0].get('corrected_plate') if vehicles else 'N/A'}")
    print("============================================================")

if __name__ == "__main__":
    benchmark_jetson()
