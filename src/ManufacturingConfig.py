import cv2
import numpy as np
import glob
import yaml
import os

# Set chessboard size
chessboard_size = (9, 6)

# Prepare object points like (0,0,0), (1,0,0), ..., (8,5,0)
objp = np.zeros((chessboard_size[0]*chessboard_size[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:chessboard_size[0], 0:chessboard_size[1]].T.reshape(-1, 2)

objpoints = []  # 3D points in real world space
imgpoints = []  # 2D points in image plane

# Load all calibration images
images = glob.glob('calibration_images/*.jpg')  # update path accordingly

if not images:
    raise FileNotFoundError("No calibration images found in 'calibration_images' directory")

# Store the first valid image size for later use
first_valid_image = None

for fname in images:
    img = cv2.imread(fname)
    if img is None:
        print(f"Warning: Could not read image {fname}")
        continue
        
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Store the first valid image size
    if first_valid_image is None:
        first_valid_image = gray.shape[::-1]

    # Find the chessboard corners
    ret, corners = cv2.findChessboardCorners(gray, chessboard_size, None)

    if ret:
        objpoints.append(objp)
        imgpoints.append(corners)

        # Optional: Draw and display the corners
        img = cv2.drawChessboardCorners(img, chessboard_size, corners, ret)
        cv2.imshow('Chessboard', img)
        cv2.waitKey(100)

cv2.destroyAllWindows()

if not objpoints or not imgpoints:
    raise ValueError("No valid chessboard patterns found in the calibration images")

if first_valid_image is None:
    raise ValueError("No valid images were processed")

# Calibrate camera
ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(
    objpoints, imgpoints, first_valid_image, None, None)

# Ensure config directory exists
os.makedirs('config', exist_ok=True)

# Load existing config or create new one
config_path = 'config/config.yaml'
if os.path.exists(config_path):
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
else:
    config = {'camera': {}}

# Update camera parameters in config
config['camera']['matrix'] = camera_matrix.tolist()
config['camera']['distortion'] = dist_coeffs.tolist()

# Save updated config
with open(config_path, 'w') as file:
    yaml.dump(config, file, default_flow_style=False)

print("Camera calibration parameters have been updated in config.yaml")

# Optional: Test the calibration
test_image = 'calibration_images/sample.jpg'
if os.path.exists(test_image):
    img = cv2.imread(test_image)
    h, w = img.shape[:2]

    new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, dist_coeffs, (w, h), 1, (w, h))

    # Undistort
    undistorted = cv2.undistort(img, camera_matrix, dist_coeffs, None, new_camera_matrix)

    cv2.imshow("Original", img)
    cv2.imshow("Undistorted", undistorted)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
else:
    print("Warning: Test image not found, skipping calibration test")
