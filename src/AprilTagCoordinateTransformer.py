"""
This script contains a class that performs AprilTag detection and converts pixel coordinates
to real-world coordinates. The class takes a camera image as input, performs AprilTag detection,
and converts the given pixel x,y position to a position in real space.

The script expects:
- A camera image containing four AprilTags
- Pixel coordinates to convert to real-world coordinates
- A configuration file with AprilTag positions and camera parameters

When run as main, the class is tested with a sample image.
"""

import cv2
import numpy as np
import yaml
from dataclasses import dataclass
from typing import Tuple, Dict, Optional, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AprilTagInfo:
    """Data class to store AprilTag information."""
    id: int
    position: np.ndarray
    rotation: np.ndarray
    corners: Optional[np.ndarray] = None

class AprilTagError(Exception):
    """Custom exception for AprilTag-related errors."""
    pass

class AprilTagCoordinateTransformer:
    def __init__(self, config_path: str):
        """
        Initialize the AprilTagCoordinateTransformer class.
        
        Args:
            config_path (str): Path to the configuration file
        """
        self.config = self._load_config(config_path)
        self.april_tags: Dict[int, AprilTagInfo] = self._initialize_april_tags()
        # Initialize AprilTag detector
        self.detector = cv2.aruco.ArucoDetector(
            cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_36h11)
        )
        
    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            raise AprilTagError(f"Failed to load config file: {str(e)}")
    
    def _initialize_april_tags(self) -> Dict[int, AprilTagInfo]:
        """Initialize AprilTag information from config."""
        tags = {}
        for tag_key, tag_data in self.config['april_tags'].items():
            tag_id = tag_data['id']
            tags[tag_id] = AprilTagInfo(
                id=tag_id,
                position=np.array(tag_data['position']),
                rotation=np.array(tag_data['rotation'])
            )
        return tags
    
    def detect_april_tags(self, image: np.ndarray) -> List[AprilTagInfo]:
        """
        Detect AprilTags in the given image.
        
        Args:
            image (np.ndarray): Input camera image
            
        Returns:
            List[AprilTagInfo]: List of detected AprilTags with their information
        """
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            corners, ids, _ = self.detector.detectMarkers(gray)
            
            if ids is None:
                logger.warning("No AprilTags detected")
                return []
            
            detected_tags = []
            for tag_corners, tag_id in zip(corners, ids):
                tag_id = tag_id[0]  # OpenCV returns ids as 2D array
                if tag_id in self.april_tags:
                    tag_info = self.april_tags[tag_id]
                    tag_info.corners = tag_corners[0]  # OpenCV returns corners as 3D array
                    detected_tags.append(tag_info)
            
            if len(detected_tags) < 4:
                logger.warning(f"Only {len(detected_tags)} AprilTags detected, expected 4")
            
            return detected_tags
            
        except Exception as e:
            raise AprilTagError(f"Error during AprilTag detection: {str(e)}")
    
    def pixel_to_real_world(self, 
                          image: np.ndarray, 
                          pixel_coords: Tuple[float, float]) -> Tuple[float, float, float]:
        """
        Convert pixel coordinates to real-world coordinates.
        
        Args:
            image (np.ndarray): Input camera image
            pixel_coords (Tuple[float, float]): Pixel coordinates (x, y)
            
        Returns:
            Tuple[float, float, float]: Real-world coordinates (x, y, z)
        """
        try:
            detected_tags = self.detect_april_tags(image)
            if len(detected_tags) < 4:
                raise AprilTagError("Not enough AprilTags detected for coordinate transformation")
            
            # Get camera matrix and distortion coefficients from config
            camera_matrix = np.array(self.config['camera']['matrix'])
            dist_coeffs = np.array(self.config['camera']['distortion'])
            
            # Create object points and image points for PnP
            obj_points = []
            img_points = []
            
            for tag in detected_tags:
                obj_points.append(tag.position)
                img_points.append(tag.corners[0])  # Use first corner of each tag
            
            obj_points = np.array(obj_points, dtype=np.float32)
            img_points = np.array(img_points, dtype=np.float32)
            
            # Solve PnP to get camera pose
            success, rvec, tvec = cv2.solvePnP(
                obj_points, img_points, camera_matrix, dist_coeffs
            )
            
            if not success:
                raise AprilTagError("Failed to solve PnP")
            
            # Convert pixel coordinates to real-world coordinates
            pixel_point = np.array([pixel_coords[0], pixel_coords[1], 1.0])
            camera_matrix_inv = np.linalg.inv(camera_matrix)
            
            # Transform pixel coordinates to camera coordinates
            camera_point = camera_matrix_inv @ pixel_point
            
            # Transform camera coordinates to world coordinates
            R, _ = cv2.Rodrigues(rvec)
            world_point = R.T @ (camera_point - tvec)
            
            return tuple(world_point.flatten())
            
        except Exception as e:
            raise AprilTagError(f"Error during coordinate transformation: {str(e)}")
    
    def visualize_results(self, 
                         image: np.ndarray, 
                         pixel_coords: Tuple[float, float],
                         real_world_coords: Optional[Tuple[float, float, float]] = None) -> np.ndarray:
        """
        Visualize the detected AprilTags and calculated real-world position.
        
        Args:
            image (np.ndarray): Input camera image
            pixel_coords (Tuple[float, float]): Original pixel coordinates
            real_world_coords (Optional[Tuple[float, float, float]]): Calculated real-world coordinates
            
        Returns:
            np.ndarray: Image with visualization
        """
        try:
            vis_image = image.copy()
            
            # Draw detected AprilTags
            detected_tags = self.detect_april_tags(image)
            
            # Add status message
            if len(detected_tags) == 0:
                status_text = "No AprilTags detected"
                status_color = (0, 0, 255)  # Red
            elif len(detected_tags) < 4:
                status_text = f"Warning: Only {len(detected_tags)} AprilTags detected (need 4)"
                status_color = (0, 165, 255)  # Orange
            else:
                status_text = f"Successfully detected {len(detected_tags)} AprilTags"
                status_color = (0, 255, 0)  # Green
            
            # Draw status message
            cv2.putText(vis_image, status_text, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
            
            # Draw detected tags if any
            for tag in detected_tags:
                if tag.corners is not None:
                    corners = tag.corners.astype(int)
                    cv2.polylines(vis_image, [corners], True, (0, 255, 0), 2)
                    cv2.putText(vis_image, f"Tag {tag.id}", 
                              tuple(corners[0]), cv2.FONT_HERSHEY_SIMPLEX, 
                              0.5, (0, 255, 0), 2)
            
            # Draw pixel coordinates
            cv2.circle(vis_image, (int(pixel_coords[0]), int(pixel_coords[1])), 
                      5, (0, 0, 255), -1)
            
            # Draw real-world coordinates if available
            if real_world_coords is not None:
                coord_text = f"World: ({real_world_coords[0]:.2f}, {real_world_coords[1]:.2f}, {real_world_coords[2]:.2f})"
                cv2.putText(vis_image, coord_text, (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            return vis_image
            
        except Exception as e:
            raise AprilTagError(f"Error during visualization: {str(e)}")

def main():
    """Test the AprilTagCoordinateTransformer class."""
    try:
        # Initialize transformer
        transformer = AprilTagCoordinateTransformer("config/config.yaml")
        
        # Load test image (replace with your test image)
        test_image = cv2.imread("test_images/test_image.jpg")
        if test_image is None:
            raise AprilTagError("Failed to load test image")
        
        # Test pixel coordinates (replace with your test coordinates)
        test_pixel_coords = (320, 240)
        
        try:
            # Try to convert to real-world coordinates
            real_world_coords = transformer.pixel_to_real_world(test_image, test_pixel_coords)
            print(f"Real-world coordinates: {real_world_coords}")
        except AprilTagError as e:
            logger.warning(f"Could not calculate real-world coordinates: {str(e)}")
            real_world_coords = None
        
        # Visualize results (will show image even if no tags detected)
        result_image = transformer.visualize_results(test_image, test_pixel_coords, real_world_coords)
        
        # Display results
        cv2.imshow("AprilTag Detection Results", result_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")

if __name__ == "__main__":
    main()




