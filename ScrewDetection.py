from ultralytics import YOLO

# Load ONNX model
model_path = 'runs/detect/yolo11n_1000epochs_run2/weights/best.pt'
model = YOLO(model_path)

# Image Path:
# Load via rest api from the camera!
image_path = "test_images/20_05_2025_Kamera von Fabian Wurmer/0.jpeg"

# Get the resulting boxes:
results = model(image_path)
for box in results[0].boxes:
    cls_id = int(box.cls[0])
    score = float(box.conf[0])
    x1, y1, x2, y2 = map(int, box.xyxy[0])
    print(f"Class {cls_id} with confidence {score:.2f} at [{x1}, {y1}, {x2}, {y2}]")
