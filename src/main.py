"""
Ruft die April Tag detection und die Screw detection auf und nutzt die damit ermittelten Schraubenpositionen um den Roboter anzusteuern.
Gibt die Positionen der Schrauben in Relation zum Koordinatensystem des Roboters auf der Konsole aus.
"""

from ScrewDetection import ScrewDetector
from CameraCapture import CameraCapture
from AprilTagCoordinateTransformer import AprilTagCoordinateTransformer
from MoveRobot import MoveRobot
import cv2
import time

def main(test_mode=False, test_image="test_image_screw.jpg"):
    # Initialize components
    detector = ScrewDetector()
    camera = CameraCapture(test_mode=test_mode, test_image=test_image)
    transformer = AprilTagCoordinateTransformer(config_path="config/config.yaml")
    robot = MoveRobot()

    try:
        # Capture image
        frame = camera.capture_image()
        
        # Detect screws
        detections = detector.detect_screws(frame)
        
        # Create a copy of the frame for visualization
        vis_image = frame.copy()
        
        # Transform coordinates and visualize screws
        for det in detections:
            # Calculate center point of bounding box
            x1, y1, x2, y2 = det['bbox']
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2
            
            # Transform pixel coordinates to real-world coordinates
            transformed_coords = transformer.pixel_to_real_world(frame, (center_x, center_y))
            print(f"Transformed coordinates for screw: {transformed_coords}")
            
            # Draw screw bounding box and label
            cv2.rectangle(vis_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            label = f"Screw: {det['confidence']:.2f}"
            cv2.putText(vis_image, label, (x1, y1-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Draw center point
            cv2.circle(vis_image, (int(center_x), int(center_y)), 
                      5, (0, 0, 255), -1)
            
            # Draw real-world coordinates
            coord_text = f"World: ({transformed_coords[0]:.2f}, {transformed_coords[1]:.2f}, {transformed_coords[2]:.2f})"
            cv2.putText(vis_image, coord_text, (x1, y2+20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            
            # Remove the screw if coordinates are valid
            if all(coord is not None for coord in transformed_coords):
                print(f"\nAttempting to remove screw at coordinates: {transformed_coords}")
                success = robot.remove_screw(*transformed_coords)
                if success:
                    print("Screw removal successful!")
                else:
                    print("Screw removal failed!")
                time.sleep(1)  # Small delay between screws
        
        # Add screw detection status message
        if len(detections) == 0:
            screw_status = "No screws detected"
            screw_status_color = (0, 0, 255)  # Red
        else:
            screw_types = set(det['class_id'] for det in detections)
            screw_status = f"Detected {len(detections)} screws of type(s): {', '.join(map(str, screw_types))}"
            screw_status_color = (0, 255, 0)  # Green
        
        # Draw screw detection status message
        cv2.putText(vis_image, screw_status, (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, screw_status_color, 2)
        
        # Visualize AprilTags
        try:
            detected_tags = transformer.detect_april_tags(frame)
            
            # Add AprilTag status message
            if len(detected_tags) == 0:
                status_text = "No AprilTags detected"
                status_color = (0, 0, 255)  # Red
            elif len(detected_tags) < 4:
                status_text = f"Warning: Only {len(detected_tags)} AprilTags detected (need 4)"
                status_color = (0, 165, 255)  # Orange
            else:
                status_text = f"Successfully detected {len(detected_tags)} AprilTags"
                status_color = (0, 255, 0)  # Green
            
            # Draw AprilTag status message
            cv2.putText(vis_image, status_text, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
            
            # Draw detected AprilTags
            for tag in detected_tags:
                if tag.corners is not None:
                    corners = tag.corners.astype(int)
                    cv2.polylines(vis_image, [corners], True, (255, 0, 0), 2)
                    cv2.putText(vis_image, f"Tag {tag.id}", 
                              tuple(corners[0]), cv2.FONT_HERSHEY_SIMPLEX, 
                              0.5, (255, 0, 0), 2)
        except Exception as e:
            # If AprilTag detection fails, still show the visualization
            cv2.putText(vis_image, "AprilTag detection failed", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Show the combined visualization
        cv2.imshow('Combined Detection Results', vis_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
            
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        camera.close()
        robot.cleanup()

if __name__ == "__main__":
    # Set test_mode=True to use test images instead of camera
    # Specify which test image to use
    main(test_mode=True, test_image="apriltags.jpg")

