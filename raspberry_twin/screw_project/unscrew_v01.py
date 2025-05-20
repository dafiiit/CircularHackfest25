from hardware_interface.pwm import PWMChannel
import time
import numpy as np
from opcua.franka_opcua import FrankaOPCUA

'''
0. Go to home position
1. Go to python defined XYZ coordinates
2. Execute some unscrewing modelled in GUI + Motor-Control
3. Go to home position

'''

franka = FrankaOPCUA(
        endpoint="opc.tcp://robot.franka.de:4840/",
        username="leop",
        password="franka123"
    )

#Never exceed 0.194 with Z coordinate!!

X_HOME = 0.35
Y_HOME = 0.0
Z_HOME = 0.19

x_target = 0.50
y_target = -0.10
z_target = 0.10

# Define home pose
home_pose = np.array([
    [1.0,  0.0,  0.0,  X_HOME],
    [0.0, -1.0,  0.0,  Y_HOME],
    [0.0,  0.0, -1.0,  Z_HOME],
    [0.0,  0.0,  0.0,  1.0]
])

# Define target pose
target_pose = np.array([
    [1.0,  0.0,  0.0,  x_target],
    [0.0, -1.0,  0.0,  y_target],
    [0.0,  0.0, -1.0,  z_target],
    [0.0,  0.0,  0.0,  1.0]
])


def main():
    # Move to home pose
    print("\nMoving to home pose...")
    franka.move_to_pose(home_pose)
    
    # Move to target pose
    print("\nMoving to target pose...")
    franka.move_to_pose(target_pose)
    
    # Return to home pose
    print("\nReturning to home pose...")
    franka.move_to_pose(home_pose)


if __name__ == "__main__":
    main()


