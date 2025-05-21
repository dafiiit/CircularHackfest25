import pyrealsense2 as rs
import numpy as np
from PIL import Image
from ultralytics import YOLO

# Initialize RealSense pipeline
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
pipeline.start(config)

# Warm-up frames
for _ in range(5):
    pipeline.wait_for_frames()

# Capture one frame
frames = pipeline.wait_for_frames()
color_frame = frames.get_color_frame()

if not color_frame:
    print("Failed to get color frame.")
    pipeline.stop()
    exit()

# Convert frame to numpy array
color_image = np.asanyarray(color_frame.get_data())  # shape (480, 640, 3), dtype=uint8, BGR format

# Convert BGR to RGB (since Pillow expects RGB)
color_image_rgb = color_image[:, :, ::-1]

# Create a PIL Image from the numpy array
img = Image.fromarray(color_image_rgb)

# Save the image to disk (optional)
img.save("snapshot.png")

# Load your YOLO model
#model = YOLO("yolov8n.pt")  # or your custom model

# YOLO expects a numpy array in BGR or RGB; Ultralityics YOLO accepts numpy RGB or BGR
# We can directly pass numpy array from Pillow
#img_np = np.array(img)  # This is RGB

# Run inference
#results = model(img_np)

# Print or process results as needed
#print(results)

# Stop the camera
#pipeline.stop()
