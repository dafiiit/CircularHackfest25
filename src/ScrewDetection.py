from ultralytics import YOLO
import cv2
import numpy as np

class ScrewDetector:
    def __init__(self, model_path='config/best-yolo11x-augmented.pt'):
        """Initialize the screw detector with a YOLO model."""
        self.model = YOLO(model_path)
    
    def detect_screws(self, image_path):
        """
        Detect screws in an image and return their positions.
        
        Args:
            image_path: Path to the image or image array
            
        Returns:
            list: List of dictionaries containing screw information (class_id, confidence, bbox)
        """
        results = self.model(image_path)
        detections = []
        
        for box in results[0].boxes:
            cls_id = int(box.cls[0])
            score = float(box.conf[0])
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            detections.append({
                'class_id': cls_id,
                'confidence': score,
                'bbox': (x1, y1, x2, y2)
            })
        
        return detections
    
    def visualize_detections(self, image_path, detections):
        """
        Visualize the detected screws on the image.
        
        Args:
            image_path: Path to the image or image array
            detections: List of detection dictionaries from detect_screws()
        """
        # Read the image
        if isinstance(image_path, str):
            image = cv2.imread(image_path)
        else:
            image = image_path.copy()
            
        # Draw bounding boxes and labels
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            confidence = det['confidence']
            
            # Draw rectangle
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Add label
            label = f"Schraube: {confidence:.2f}"
            cv2.putText(image, label, (x1, y1-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Show the image
        cv2.imshow('Screw Detection Results', image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

def main():
    # Initialize detector
    detector = ScrewDetector()
    
    # Image path
    image_path = "test_images/apriltags.jpg"
    
    # Detect screws
    detections = detector.detect_screws(image_path)
    
    # Print results
    for det in detections:
        print(f"Class {det['class_id']} with confidence {det['confidence']:.2f} "
              f"at {det['bbox']}")
    
    # Visualize results
    detector.visualize_detections(image_path, detections)

if __name__ == "__main__":
    main()
