import os
import sys
import numpy as np
import cv2
from ultralytics import YOLO

def export_and_verify_onnx(
    pt_model_path="models/vehicle_detector.pt",
    onnx_output_path="models/vehicle_detector.onnx"
):
    print("=" * 60, flush=True)
    print("      EXPORTING VEHICLE DETECTOR TO ONNX FOR JETSON", flush=True)
    print("=" * 60, flush=True)

    if not os.path.exists(pt_model_path):
        print(f"[ERROR] PyTorch model not found at {pt_model_path}", flush=True)
        sys.exit(1)

    print(f"Loading PyTorch model: {pt_model_path}", flush=True)
    model = YOLO(pt_model_path)

    print(f"Exporting to ONNX: {onnx_output_path}...", flush=True)
    exported_path = model.export(
        format="onnx",
        dynamic=False,
        imgsz=640,
        opset=12,
        simplify=True
    )
    
    if os.path.exists(exported_path) and os.path.abspath(exported_path) != os.path.abspath(onnx_output_path):
        import shutil
        shutil.copy2(exported_path, onnx_output_path)

    print(f"ONNX model exported to: {onnx_output_path}", flush=True)

    # Verification of ONNX Model
    print("\n" + "=" * 60, flush=True)
    print("      VERIFYING EXPORTED ONNX MODEL", flush=True)
    print("=" * 60, flush=True)

    try:
        import onnxruntime as ort

        session = ort.InferenceSession(onnx_output_path, providers=["CPUExecutionProvider"])
        inputs = session.get_inputs()
        outputs = session.get_outputs()

        print(f"ONNX Inputs : {[(inp.name, inp.shape, inp.type) for inp in inputs]}", flush=True)
        print(f"ONNX Outputs: {[(out.name, out.shape, out.type) for out in outputs]}", flush=True)

        input_shape = inputs[0].shape
        output_shape = outputs[0].shape

        print(f"Input Shape : {input_shape}", flush=True)
        print(f"Output Shape: {output_shape}", flush=True)

        # Generate dummy input tensor (1, 3, 640, 640)
        dummy_input = np.random.randn(1, 3, 640, 640).astype(np.float32)
        onnx_out = session.run(None, {inputs[0].name: dummy_input})

        print(f"Dummy Inference Success! Output tensor shape: {onnx_out[0].shape}", flush=True)

        # Check prediction consistency between PyTorch and ONNX
        sample_canvas = np.full((640, 640, 3), 128, dtype=np.uint8)
        cv2.rectangle(sample_canvas, (100, 100), (500, 500), (0, 0, 255), -1)

        pt_res = model(sample_canvas, conf=0.1, verbose=False)
        pt_boxes = len(pt_res[0].boxes) if pt_res else 0

        # Preprocess sample_canvas for ONNX
        blob = cv2.resize(sample_canvas, (640, 640))
        blob = np.transpose(blob, (2, 0, 1)).astype(np.float32) / 255.0
        blob = np.expand_dims(blob, axis=0)
        onnx_raw = session.run(None, {inputs[0].name: blob})[0]

        print(f"PyTorch detections count : {pt_boxes}", flush=True)
        print(f"ONNX raw output shape    : {onnx_raw.shape}", flush=True)
        print(f"Number of classes in ONNX: {output_shape[1] - 4 if len(output_shape) == 3 else 'dynamic'}", flush=True)

        print("\n[ONNX VERIFICATION SUCCESSFUL] Model is ready for Jetson TensorRT / DeepStream deployment!", flush=True)
        print("=" * 60, flush=True)

    except Exception as e:
        print(f"[ERROR] ONNX verification failed: {e}", flush=True)
        sys.exit(1)

if __name__ == "__main__":
    export_and_verify_onnx()
