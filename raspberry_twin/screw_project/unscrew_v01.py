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

#Never exceed 0.194 with Z coordinate!!

X_HOME = 0.35
Y_HOME = 0.0
Z_HOME = 0.19

x_target = 0.549
y_target = 0.214
z_target = 0.125

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
        
        # wait until screw_status is set to 3 by robot
        print("Waiting for value to be 3..")
        while value != 3:
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
