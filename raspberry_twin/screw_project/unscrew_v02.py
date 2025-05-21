from hardware_interface.pwm import PWMChannel
import time
import numpy as np
from opcua_interface.franka_opcua import FrankaOPCUA
import sys
import signal

'''
0. Go to home position
1. Go to python defined XYZ coordinates
2. Execute some unscrewing modelled in GUI + Motor-Control
3. Go to home position

'''

franka = FrankaOPCUA(
    endpoint="opc.tcp://192.168.136.1:4840/",
    username="leop",
    password="franka123"
)

pwm_motor = PWMChannel(chip=0, channel=1, gpio_pin=13, frequency_hz=50)
pwm_motor.enable()

pwm_motor.set_duty_cycle_percent(7.5)
print("Giving 10 seconds for controller to be switched on..")
time.sleep(10.0)
print("Setup complete. Start Execution")

'''
Pose 1:
 [[ 9.99999981e-01  6.22141348e-05 -1.10247808e-05  5.18419185e-01]
 [ 6.22143506e-05 -9.99999981e-01  1.95774384e-05  1.51609179e-01]
 [-1.10235626e-05 -1.95781240e-05 -1.00000000e+00  1.19982699e-01]
 [ 0.00000000e+00  0.00000000e+00  0.00000000e+00  1.00000000e+00]]
'''

#Never exceed 0.194 with Z coordinate!!

X_HOME = 0.35
Y_HOME = 0.0
Z_HOME = 0.19

x_target = 0.5185
y_target = 0.1517
z_target = 0.12

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


def signal_handler(sig, frame):
    print("\nShutting down gracefully...")
    if 'franka' in globals():
        franka.disconnect()
    if 'pwm_motor' in globals():
        pwm_motor.set_duty_cycle_percent(7.5)
        pwm_motor.cleanup()
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        key = "screw_status"

        # set screw_status to 0 initially
        value = 0
        franka.set_key_value(key, value)
        # wait until screw_status is set to 1 by robot (home-position reached)
        print("Waiting for value to be 1..")
        while value != 1:
            value = franka.get_key_value(key)
            time.sleep(0.1)
        
        # go to target position
        print("\nMoving to target pose...")
        franka.move_to_pose(target_pose)
        time.sleep(1.0)  # just to make sure
        
        # start motor slowly
        pwm_motor.set_duty_cycle_percent(8.5)
        time.sleep(0.5)
        
        # set screw_status to 2 when pwm is running
        franka.set_key_value(key, 2)

        #robot now applies 1N in Z until screw_status is set to 5
        print("Applying 1 N..")
        while value != 5:
            pose = franka.get_pose()
            time.sleep(0.05)
            value = 5
        franka.set_key_value(key, value)

        #wait for desk-loop to finish!
        print("Waiting for value to be 3..")
        while value != 3:
            value = franka.get_key_value(key)
            time.sleep(0.1)

        #robot now applies 5N in Z until screw_status is set to 6
        print("Applying 5 N..")
        while value != 6:
            pose = franka.get_pose()
            time.sleep(0.05)
            value = 6
        franka.set_key_value(key, value)

        #wait for desk-loop to finish!
        print("Waiting for value to be 4..")
        while value != 4:
            value = franka.get_key_value(key)
            time.sleep(0.1)

        # wait until screw_status is set to 3 by robot
        print("Waiting for value to be 7..")
        while value != 7:
            value = franka.get_key_value(key)
            time.sleep(0.1)
        
        # stop screwing
        pwm_motor.set_duty_cycle_percent(7.5)
        
    finally:
        # Ensure cleanup happens even if an exception occurs
        franka.disconnect()
        pwm_motor.set_duty_cycle_percent(7.5)
        pwm_motor.cleanup()
        print("Finished!")

if __name__ == "__main__":
    main()
