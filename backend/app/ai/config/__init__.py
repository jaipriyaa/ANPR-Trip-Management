import os
from typing import Dict, List, Tuple

# Base paths
AI_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(AI_DIR, "weights")
BACKEND_DIR = os.path.dirname(os.path.dirname(AI_DIR))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
DEBUG_DIR = os.path.join(PROJECT_ROOT, "debug")
ROOT_MODELS_DIR = os.path.join(PROJECT_ROOT, "models")

os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(DEBUG_DIR, exist_ok=True)
os.makedirs(ROOT_MODELS_DIR, exist_ok=True)

# Configurable Inference Backends & Hardware
MODEL_BACKEND = os.getenv("MODEL_BACKEND", "AUTO").upper()
GPU_ENABLED = os.getenv("GPU_ENABLED", "true").lower() in ("true", "1", "yes")
GPU_DEVICE = int(os.getenv("GPU_DEVICE", "0"))

ONNX_MODEL_DIR_ENV = os.getenv("ONNX_MODEL_PATH")
ONNX_DIR = ONNX_MODEL_DIR_ENV if (ONNX_MODEL_DIR_ENV and os.path.isdir(ONNX_MODEL_DIR_ENV)) else ROOT_MODELS_DIR

TRT_ENGINE_DIR_ENV = os.getenv("TENSORRT_ENGINE_PATH")
TENSORRT_DIR = TRT_ENGINE_DIR_ENV if (TRT_ENGINE_DIR_ENV and os.path.isdir(TRT_ENGINE_DIR_ENV)) else ROOT_MODELS_DIR

# Vehicle detection settings
VEHICLE_DETECTION_MODEL_ENGINE = os.path.join(TENSORRT_DIR, "vehicle_detector.engine")
if not os.path.exists(VEHICLE_DETECTION_MODEL_ENGINE):
    VEHICLE_DETECTION_MODEL_ENGINE = os.path.join(MODEL_DIR, "vehicle_detector.engine")

VEHICLE_DETECTION_MODEL_ONNX = os.path.join(ONNX_DIR, "vehicle_detector.onnx")
if not os.path.exists(VEHICLE_DETECTION_MODEL_ONNX):
    VEHICLE_DETECTION_MODEL_ONNX = os.path.join(MODEL_DIR, "vehicle_detector.onnx")

ENV_VEHICLE_PT = os.getenv("VEHICLE_MODEL_PATH")
ROOT_VEHICLE_DETECTOR_PT = os.path.join(ROOT_MODELS_DIR, "vehicle_detector.pt")
ROOT_YOLO11_PT = os.path.join(PROJECT_ROOT, "backend", "yolo11n.pt")
ROOT_YOLOV8_PT = os.path.join(PROJECT_ROOT, "backend", "yolov8n.pt")

if ENV_VEHICLE_PT and os.path.exists(ENV_VEHICLE_PT):
    VEHICLE_DETECTION_MODEL_PT = ENV_VEHICLE_PT
elif os.path.exists(ROOT_VEHICLE_DETECTOR_PT):
    VEHICLE_DETECTION_MODEL_PT = ROOT_VEHICLE_DETECTOR_PT
elif os.path.exists(os.path.join(MODEL_DIR, "vehicle_detector.pt")):
    VEHICLE_DETECTION_MODEL_PT = os.path.join(MODEL_DIR, "vehicle_detector.pt")
elif os.path.exists(ROOT_YOLO11_PT):
    VEHICLE_DETECTION_MODEL_PT = ROOT_YOLO11_PT
elif os.path.exists(ROOT_YOLOV8_PT):
    VEHICLE_DETECTION_MODEL_PT = ROOT_YOLOV8_PT
else:
    VEHICLE_DETECTION_MODEL_PT = os.path.join(ROOT_MODELS_DIR, "vehicle_detector.pt")

VEHICLE_CONF_THRESHOLD = float(os.getenv("VEHICLE_DETECTION_CONFIDENCE", os.getenv("VEHICLE_CONF_THRESHOLD", "0.35")))
VEHICLE_IOU_THRESHOLD = float(os.getenv("VEHICLE_DETECTION_IOU", os.getenv("VEHICLE_IOU_THRESHOLD", "0.45")))
imgsz_env = int(os.getenv("VEHICLE_DETECTION_IMAGE_SIZE", os.getenv("VEHICLE_IMGSZ", "640")))
VEHICLE_IMGSZ: Tuple[int, int] = (imgsz_env, imgsz_env)

# Class mapping for custom 4-class trained vehicle detector (0=Car, 1=Motorcycle, 2=Bus, 3=Truck)
COCO_VEHICLE_CLASSES = {
    0: "Car",
    1: "Motorcycle",
    2: "Bus",
    3: "Truck",
}

# Color mapping (BGR format for OpenCV) for each vehicle type
VEHICLE_CLASS_COLORS: Dict[str, Tuple[int, int, int]] = {
    "Car": (255, 191, 0),          # Deep Cyan / Blue
    "SUV": (255, 128, 0),          # Azure Blue
    "Pickup Truck": (0, 215, 255),  # Gold / Amber
    "Heavy Truck": (0, 165, 255),   # Orange
    "Mini Truck": (0, 255, 255),    # Yellow
    "Bus": (211, 0, 148),          # Purple / Violet
    "Van": (50, 205, 50),          # Lime Green
    "Commercial": (147, 112, 219),  # Purple
    "Motorcycle": (0, 0, 255),      # Bright Red
    "Auto Rickshaw": (255, 105, 180), # Hot Pink
    "Vehicle": (0, 255, 0),        # Green fallback
}

PLATE_COLOR: Tuple[int, int, int] = (0, 255, 255) # Bright Yellow for Plate Bbox

# Plate detection settings
PLATE_DETECTION_MODEL_ENGINE = os.path.join(TENSORRT_DIR, "plate_detector.engine")
if not os.path.exists(PLATE_DETECTION_MODEL_ENGINE):
    PLATE_DETECTION_MODEL_ENGINE = os.path.join(MODEL_DIR, "plate_detector.engine")

PLATE_DETECTION_MODEL_ONNX = os.path.join(ROOT_MODELS_DIR, "license_plate_detector.onnx")
if not os.path.exists(PLATE_DETECTION_MODEL_ONNX):
    PLATE_DETECTION_MODEL_ONNX = os.path.join(MODEL_DIR, "plate_detector.onnx")

ENV_PLATE_PT = os.getenv("PLATE_MODEL_PATH")
if ENV_PLATE_PT and os.path.exists(ENV_PLATE_PT):
    PLATE_DETECTION_MODEL_PT = ENV_PLATE_PT
elif os.path.exists(os.path.join(ROOT_MODELS_DIR, "license_plate_detector.pt")):
    PLATE_DETECTION_MODEL_PT = os.path.join(ROOT_MODELS_DIR, "license_plate_detector.pt")
elif os.path.exists(os.path.join(MODEL_DIR, "license_plate_detector.pt")):
    PLATE_DETECTION_MODEL_PT = os.path.join(MODEL_DIR, "license_plate_detector.pt")
else:
    PLATE_DETECTION_MODEL_PT = os.path.join(ROOT_MODELS_DIR, "license_plate_detector.pt")


PLATE_CONF_THRESHOLD = 0.10
PLATE_IOU_THRESHOLD = 0.40
PLATE_IMGSZ: Tuple[int, int] = (640, 640)

# Fallback OpenCV plate detection thresholds
OPENCV_PLATE_MIN_AREA = 250
OPENCV_PLATE_ASPECT_RATIO_MIN = 1.2
OPENCV_PLATE_ASPECT_RATIO_MAX = 7.5
OPENCV_PLATE_MIN_HEIGHT = 8
OPENCV_PLATE_MIN_WIDTH = 30

# OCR Settings
OCR_CONFIDENCE_THRESHOLD = 0.10
OCR_CHAR_WHITELIST = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
OCR_BATCH_SIZE = 1
OCR_GPU = os.getenv("OCR_GPU", "true").lower() in ("true", "1", "yes")

# OCR Execution Mode: "STANDARD" or "ROBUST" (multi-variant ensemble for handwritten/irregular plates)
PLATE_OCR_MODE = os.getenv("PLATE_OCR_MODE", "ROBUST").upper()

# Branding Blacklist for Container & Vehicle Body Advertising/Text
BRANDING_BLACKLIST: List[str] = [
    "GOODS", "CARRIER", "LOGISTICS", "ASHOK", "LEYLAND", "TATA",
    "BHARATBENZ", "EICHER", "VOLVO", "SCANIA", "TRANSPORT", "TRUCK",
    "BUS", "CONTAINER", "PUBLIC", "PERMIT", "SPEED", "ALLINDIA",
    "SAFETY", "FIRST", "SALES", "INDIA", "SERVICE", "REPAIR"
]

# Preprocessing & Crop Settings
PLATE_TARGET_WIDTH = 320
PLATE_TARGET_HEIGHT = 96
PLATE_WIDTH = 320
PLATE_HEIGHT = 96
CLAHE_CLIP_LIMIT = 3.0
CLAHE_GRID_SIZE: Tuple[int, int] = (8, 8)
SHARPEN_STRENGTH = 1.0
DENOISE_STRENGTH = 10
CROP_MARGIN_PERCENT = 0.05

# Validation
VALIDATION_MIN_LENGTH = 5
VALIDATION_MAX_LENGTH = 14

# Multi-frame Tracking & Fusion Parameters
TRACKING_ENABLED = os.getenv("TRACKING_ENABLED", "true").lower() in ("true", "1", "yes")
TRACK_MAX_AGE_SECONDS = float(os.getenv("TRACK_MAX_AGE_SECONDS", "2.0"))

MULTIFRAME_ENABLED = os.getenv("MULTIFRAME_ENABLED", "true").lower() in ("true", "1", "yes")
MULTIFRAME_WINDOW_SECONDS = float(os.getenv("MULTIFRAME_WINDOW_SECONDS", "5.0"))
MULTIFRAME_MIN_OBSERVATIONS = int(os.getenv("MULTIFRAME_MIN_OBSERVATIONS", "2"))
MULTIFRAME_SIMILARITY_THRESHOLD = float(os.getenv("MULTIFRAME_SIMILARITY_THRESHOLD", "0.85"))
MULTIFRAME_MIN_CONFIDENCE = float(os.getenv("MULTIFRAME_MIN_CONFIDENCE", "0.70"))
ENTRY_DEDUP_WINDOW_SECONDS = float(os.getenv("ENTRY_DEDUP_WINDOW_SECONDS", "120.0"))

FUSION_MIN_FRAMES = int(os.getenv("FUSION_MIN_FRAMES", "2"))
FUSION_MIN_CONFIDENCE = float(os.getenv("FUSION_MIN_CONFIDENCE", "0.70"))
FUSION_WEIGHT_CONFIDENCE = float(os.getenv("FUSION_WEIGHT_CONFIDENCE", "0.60"))
FUSION_WEIGHT_FREQUENCY = float(os.getenv("FUSION_WEIGHT_FREQUENCY", "0.40"))

TRACKING_MAX_AGE = 30
TRACKING_MIN_HITS = 2
TRACKING_IOU_THRESHOLD = 0.3

# Runtime & Pipeline
AI_MODEL_VERSION = "v11.0-edge-anpr"
ENABLE_ONNX = True
ENABLE_FALLBACK = True
MAX_VIDEO_FRAMES = 60
FRAME_SKIP = int(os.getenv("FRAME_SKIP", "1"))
MAX_FPS = float(os.getenv("MAX_FPS", "30.0"))
FP16_ENABLED = os.getenv("FP16_ENABLED", "true").lower() in ("true", "1", "yes")

# Character confusion matrix for correction
CHAR_CONFUSIONS: Dict[str, List[str]] = {
    "0": ["O", "Q", "D", "U"],
    "O": ["0", "Q", "D", "U"],
    "1": ["I", "L", "T"],
    "I": ["1", "L", "T"],
    "2": ["Z"],
    "Z": ["2"],
    "5": ["S"],
    "S": ["5"],
    "6": ["G", "C"],
    "G": ["6", "C"],
    "8": ["B", "3"],
    "B": ["8", "3"],
    "9": ["g"],
}
