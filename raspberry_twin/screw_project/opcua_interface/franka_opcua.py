import numpy as np
from scipy.spatial.transform import Rotation as R
import time
from opcua import Client, ua
from opcua.common.type_dictionary_buider import get_ua_class

class FrankaOPCUA:
    def __init__(self, endpoint, username, password):
        """
        Initialize the Franka OPC UA controller.
        
        Args:
            endpoint (str): OPC UA server endpoint (e.g., "opc.tcp://robot.franka.de:4840/")
            username (str): Username for authentication
            password (str): Password for authentication
        """
        self.client = Client(endpoint)
        self.client.set_user(username)
        self.client.set_password(password)
        self.client.connect()
        self.typedefs = self.client.load_type_definitions()
        
    def __del__(self):
        """Clean up by disconnecting the client when the object is destroyed."""
        if hasattr(self, 'client'):
            self.client.disconnect()
    
    def disconnect(self):
        if hasattr(self, "client"):
            try:
                self.client.disconnect()
                print("[OPCUA] Disconnected successfully.")
            except Exception as e:
                print(f"[OPCUA] Error during disconnect: {e}")
    
    @staticmethod
    def stack_A(R, t):
        """Create a 4x4 homogeneous transformation matrix from rotation and translation."""
        A = np.eye(4)
        A[:3, :3] = R
        A[:3, 3] = t
        return A
    
    @staticmethod
    def project_to_SE3(matrix):
        """Project a 4x4 matrix to the closest SE(3) transformation matrix."""
        if matrix.shape != (4, 4):
            raise ValueError("Input matrix must be 4x4.")
        
        A = matrix[:3, :3]
        t = matrix[:3, 3]
        
        U, S, Vt = np.linalg.svd(A)
        R = np.dot(U, Vt)
        
        if np.linalg.det(R) < 0:
            U[:, -1] *= -1
            R = np.dot(U, Vt)
        
        T = np.eye(4)
        T[:3, :3] = R
        T[:3, 3] = t
        return T
    
    def set_pose(self, pose, key="universal pose key"):
        """Set a pose in the robot's key-pose map."""
        pose_list = pose.T.flatten().tolist()
        root = self.client.get_root_node()
        robot = root.get_child("0:Objects").get_child("2:Robot")
        keyPoseMapObject = robot.get_child("2:KeyValueMaps").get_child("2:KeyPoseMap")
        setKeyPoseMethod = keyPoseMapObject.get_child("2:Replace")
        
        myKeyPosePair = get_ua_class("KeyPosePair")()
        myKeyPosePair.Key = key
        myKeyPosePair.Value = pose_list
        keyPoseMapObject.call_method(setKeyPoseMethod, ua.Variant(myKeyPosePair, ua.VariantType.ExtensionObject))
    
    def get_key_value(self, key):
        """Get a value from the KeyIntMap by its key."""
        root = self.client.get_root_node()
        robot = root.get_child("0:Objects").get_child("2:Robot")
        key_value_map = robot.get_child("2:KeyValueMaps").get_child("2:KeyIntMap")
        get_key_value_method = key_value_map.get_child("2:Read")
        return key_value_map.call_method(get_key_value_method, key)
    
    def set_key_value(self, key, value):
        """Set a key-value pair in the KeyIntMap."""
        root = self.client.get_root_node()
        robot = root.get_child("0:Objects").get_child("2:Robot")
        key_value_map = robot.get_child("2:KeyValueMaps").get_child("2:KeyIntMap")
        set_key_value_method = key_value_map.get_child("2:Replace")
        
        KeyValuePair = get_ua_class("KeyIntPair")()
        KeyValuePair.Key = key
        KeyValuePair.Value = int(value)
        key_value_map.call_method(set_key_value_method, ua.Variant(KeyValuePair, ua.VariantType.ExtensionObject))
    
    def get_pose(self):
        """Get the current Cartesian pose of the robot."""
        root = self.client.get_root_node()
        robot = root.get_child("0:Objects").get_child("2:Robot")
        executionControl = robot.get_child("2:ExecutionControl")
        cartesianPose = executionControl.get_child("2:CartesianPose")
        pose_list = cartesianPose.get_value()
        pose = np.array(pose_list)
        return pose.T
    
    @staticmethod
    def is_pose_close(current_pose, target_pose, tolerance):
        """Check if two poses are within a specified tolerance."""
        return np.allclose(current_pose, target_pose, atol=tolerance)
    
    def move_to_pose(self, target_pose, tolerance=0.002, key="universal pose key"):
        """Move the robot to a target pose with specified tolerance."""
        target_pose = self.project_to_SE3(target_pose)
        print("Setting new target pose on OPC UA server...")
        self.set_pose(target_pose, key)
        print(f"Target pose set to:\n{target_pose}")
        
        pose = self.get_pose()
        print("Moving to target pose...")
        while not self.is_pose_close(pose, target_pose, tolerance):
            time.sleep(0.1)
            pose = self.get_pose()
        
        print(f"Movement complete with tolerance of {tolerance}")
        print(f"Achieved pose:\n{pose}")
        print(f"Deviation from target pose:\n{pose-target_pose}")
        print(f"Maximum deviation: {np.max(np.abs(pose-target_pose))}")

