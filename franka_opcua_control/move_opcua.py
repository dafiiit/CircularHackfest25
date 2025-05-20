import numpy as np
from scipy.spatial.transform import Rotation as R

import cv2

import time

from opcua import Client, ua
from opcua.common.type_dictionary_buider import get_ua_class

# Configure and connect the client
client = Client("opc.tcp://robot.franka.de:4840/") # 4840 is the default OPC UA port
client.set_user("leop") # Change to your user name ...
client.set_password("franka123") # ... and password here
client.connect() # Connect our client to the robot
typedefs = client.load_type_definitions() # Load custom type definitions

def stack_A(R, t):
    A = np.eye(4)
    A[:3, :3] = R
    A[:3, 3] = t
    return A

def project_to_SE3(matrix):
    # Ensure the matrix is 4x4.
    if matrix.shape != (4, 4):
        raise ValueError("Input matrix must be 4x4.")
    
    # Extract the 3x3 rotation part and the translation vector.
    A = matrix[:3, :3]
    t = matrix[:3, 3]
    
    # Compute the SVD of the 3x3 matrix.
    U, S, Vt = np.linalg.svd(A)
    
    # Reconstruct the closest rotation matrix.
    R = np.dot(U, Vt)
    
    # Ensure a right-handed coordinate system: det(R) should be +1.
    if np.linalg.det(R) < 0:
        U[:, -1] *= -1
        R = np.dot(U, Vt)
    
    # Reconstruct the 4x4 homogeneous transformation matrix.
    T = np.eye(4)
    T[:3, :3] = R
    T[:3, 3] = t
    return T


def set_pose(client, pose, key):
    # Convert A_0TCP to list
    pose_list = pose.T.flatten().tolist() #Double Check!
    # Browse the server
    root = client.get_root_node()
    robot = root.get_child("0:Objects").get_child("2:Robot")
    keyPoseMapObject = robot.get_child("2:KeyValueMaps").get_child("2:KeyPoseMap")
    setKeyPoseMethod = keyPoseMapObject.get_child("2:Replace")
    getKeyPoseMethod = keyPoseMapObject.get_child("2:Read")

    # Create a new Key-Pose-Pair
    myKeyPosePair = get_ua_class("KeyPosePair")()
    myKeyPosePair.Key = key
    myKeyPosePair.Value = pose_list
    #print("Old Pose on Server: \n", keyPoseMapObject.call_method(getKeyPoseMethod, key))
    keyPoseMapObject.call_method(setKeyPoseMethod, ua.Variant(myKeyPosePair, ua.VariantType.ExtensionObject))
    #print("New Pose on Server: \n", keyPoseMapObject.call_method(getKeyPoseMethod, key))

def get_pose(client):
    # Browse the server
    root = client.get_root_node()
    robot = root.get_child("0:Objects").get_child("2:Robot")
    executionControl = robot.get_child("2:ExecutionControl")
    cartesianPose = executionControl.get_child("2:CartesianPose")
    pose_list = cartesianPose.get_value() # list of lists of floats
    pose = np.array(pose_list)
    pose = pose.T #Double Check!

    return pose #A_0TCP

def is_pose_close(current_pose, target_pose, tolerance):
    """
    Checks if two 4x4 matrices are close enough within a given tolerance.
    """
    return np.allclose(current_pose, target_pose, atol=tolerance)

def move_to_pose(input_target_pose, client):
    tolerance = 0.002
    target_pose = project_to_SE3(input_target_pose)
    print("setting new target pose on opc ua server...")
    set_pose(client, target_pose, "universal pose key")
    print("set new target pose on opc ua server to: \n", target_pose)
    pose = get_pose(client)
    print("moving to new target pose...")
    while not is_pose_close(pose, target_pose, tolerance):
        time.sleep(0.1)
        pose = get_pose(client)
    print(f"moved to new target pose with set tolerance of {tolerance}")
    print("achieved pose:\n", pose)
    print("deviation from target pose:\n", pose-target_pose)
    print("maximum deviation: ", np.max(np.abs(pose-target_pose)))   

def run_test_case(test_case):
    
    # Test case 0: Robot moves between home pose and target pose, then back to home pose.
    if test_case == 0:
        '''
        Note: Set Loop in GUI to 3

        - Robot goes to home pose
        - moves to target pose
        - moves back to home pose
        '''
        # Home pose matrix (robot's starting position)
        my_list_1 = [
            [0.9935455957256543, -0.10969548535194779, 0.02887932615233613, 0.0],
            [-0.10717965892994313, -0.9912025502899791, -0.0776530152779702, 0.0],
            [0.037143448204176976, 0.07405653753195755, -0.9965620871296889, 0.0],
            [0.3870164138414612, -0.13125461408807915, 0.6443084893152867, 1.0]
        ]

        # Target pose matrix (desired position to move to)
        my_list_2 = [
            [0.9973492070494834, -0.06852433347807707, 0.024473264813059985, 0.0],
            [-0.0697680718301732, -0.9960889503238824, 0.0542142505917413, 0.0],
            [0.02066255397907596, -0.05577799424505102, -0.9982293695444253, 0.0],
            [0.6924764370953914, -0.2427060527479671, 0.2511901740457925, 1.0]
        ]

        # Convert lists to numpy arrays for easier manipulation
        A_01 = np.array(my_list_1)
        A_02 = np.array(my_list_2)

        A_01 = A_01.T
        A_02 = A_02.T

        # Print both poses for the user
        print("Home-Pose: ", A_01)  # Transpose for easier reading of the matrix
        print("Target-Pose: ", A_02)  # Transpose for easier reading of the matrix
        
        # Move the robot to the home pose
        print("Moving to Home Pose...")
        move_to_pose(A_01, client)
        
        # Move the robot to the target pose
        print("Moving to Target Pose...")
        move_to_pose(A_02, client)
        
        # Move the robot back to the home pose
        print("Returning to Home Pose...")
        move_to_pose(A_01, client)

    # Test case 1: Simple movement between two poses.
    elif test_case == 1:
        '''
        t.b.d
        '''
        print("Case Not Implemented")
    else:
        print("Case Not Implemented")  
    

def main():
    '''
    Here You can Test different things
    '''

    run_test_case(0)


main()



