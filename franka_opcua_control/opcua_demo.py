import time
import numpy as np
from franka_opcua import FrankaOPCUA

# python franka_opcua_control/opcua_demo.py

def main():
    # Initialize the Franka OPC UA controller
    franka = FrankaOPCUA(
        endpoint="opc.tcp://robot.franka.de:4840/",
        username="leop",
        password="franka123"
    )
    
    example = "03"

    try:
        if example=="01":
            # Example 1: Setting and getting key-value pairs
            print("\n--- Example 1: Key-Value Operations ---")
            key = "test_key"
            
            # Set a value
            franka.set_key_value(key, 4)
            print(f"Value set to 4")
            time.sleep(10)
            
            # Update the value
            franka.set_key_value(key, 3)
            print(f"Value updated to 3")
            time.sleep(2)
            
            # Get the value
            value = franka.get_key_value(key)
            print(f"Retrieved value for {key}: {value}")
        
        elif example =="02": 
            # Example 2: Pose movement; Needs loop with count 3
            print("\n--- Example 2: Pose Movement ---")
            
            # Define home pose
            home_pose = np.array([
                [0.9935455957256543, -0.10969548535194779, 0.02887932615233613, 0.0],
                [-0.10717965892994313, -0.9912025502899791, -0.0776530152779702, 0.0],
                [0.037143448204176976, 0.07405653753195755, -0.9965620871296889, 0.0],
                [0.3870164138414612, -0.13125461408807915, 0.6443084893152867, 1.0]
            ]).T
            
            # Define target pose
            target_pose = np.array([
                [0.9973492070494834, -0.06852433347807707, 0.024473264813059985, 0.0],
                [-0.0697680718301732, -0.9960889503238824, 0.0542142505917413, 0.0],
                [0.02066255397907596, -0.05577799424505102, -0.9982293695444253, 0.0],
                [0.6924764370953914, -0.2427060527479671, 0.2511901740457925, 1.0]
            ]).T
            
            # Move to home pose
            print("\nMoving to home pose...")
            franka.move_to_pose(home_pose)
            
            # Move to target pose
            print("\nMoving to target pose...")
            franka.move_to_pose(target_pose)
            
            # Return to home pose
            print("\nReturning to home pose...")
            franka.move_to_pose(home_pose)

        elif example =="03": 
            # Example 2: Pose movement; Needs loop with count 3
            print("\n--- Example 2: Pose Movement ---")
            
            # Define home pose
            home_pose = np.array([
                [1.0, 0.0, 0.0, 0.0],
                [0.0, -1.0, 0.0, 0.0],
                [0.0, 0.0, -1.0, 0.0],
                [0.38, -0.13, 0.64, 1.0]
            ]).T
            
            # Define target pose
            target_pose = np.array([
                [1.0, 0.0, 0.0, 0.0],
                [0.0, -1.0, 0.0, 0.0],
                [0.0, 0.0, -1.0, 0.0],
                [0.38, -0.13, 0.70, 1.0]
            ]).T
            
            # Move to home pose
            print("\nMoving to home pose...")
            franka.move_to_pose(home_pose)
            
            # Move to target pose
            print("\nMoving to target pose...")
            franka.move_to_pose(target_pose)
            
            # Return to home pose
            print("\nReturning to home pose...")
            franka.move_to_pose(home_pose)
        else:
            print("Example not implemented")
        
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # The destructor will handle disconnection
        pass

if __name__ == "__main__":
    main()