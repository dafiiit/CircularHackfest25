"""
Ruft die April Tag detection und die Screw detection auf und nutzt die damit ermittelten Schraubenpositionen um den Roboter anzusteuern.
Gibt die Positionen der Schrauben in Relation zum Koordinatensystem des Roboters auf der Konsole aus.
"""

from ScrewDetection import ScrewDetector
from CameraCapture import CameraCapture
from AprilTagCoordinateTransformer import AprilTagCoordinateTransformer

def main():
    # Initialize components
    detector = ScrewDetector()
    camera = CameraCapture()
    transformer = AprilTagCoordinateTransformer()

    try:
        # Capture image
        frame = camera.capture_image()
        
        # Detect screws
        detections = detector.detect_screws(frame)
        
        # Transform coordinates
        for det in detections:
            transformed_coords = transformer.transform_coordinates(det['bbox'])
            print(f"Transformed coordinates for screw: {transformed_coords}")
            
        # Visualize results
        detector.visualize_detections(frame, detections)
            
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        camera.close()

if __name__ == "__main__":
    main()

