"""
Diese Datei enthält eine Klasse, die den Roboter so ansteuert.
Dabei soll die Schraubenposition übergeben werden und der Roboter schraubt entfernt dann automatisch die Schraube an dieser Position.

Diese Datei  müssen wir noch testen.
"""

import time
import numpy as np
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Franka_Communication.raspberry_twin.screw_project.opcua_interface.franka_opcua import FrankaOPCUA
import socket
from Franka_Communication.raspberry_twin.screw_project.hardware_interface.pwm import PWMChannel
import signal

class MoveRobot:
    def __init__(self, endpoint="opc.tcp://192.168.136.1:4840/", 
                 username="leop", password="franka123"):
        """Initialize the robot control system."""
        self.franka = FrankaOPCUA(
            endpoint=endpoint,
            username=username,
            password=password
        )
        
        # Initialize PWM motor
        self.pwm_motor = PWMChannel(chip=0, channel=1, gpio_pin=13, frequency_hz=50)
        self.pwm_motor.enable()
        self.pwm_motor.set_duty_cycle_percent(7.5)
        
        # Home position coordinates
        self.X_HOME = 0.35
        self.Y_HOME = 0.0
        self.Z_HOME = 0.19
        
        # Safety limit for Z coordinate
        self.MAX_Z = 0.194
        
        # Initialize home pose
        self.home_pose = np.array([
            [1.0,  0.0,  0.0,  self.X_HOME],
            [0.0, -1.0,  0.0,  self.Y_HOME],
            [0.0,  0.0, -1.0,  self.Z_HOME],
            [0.0,  0.0,  0.0,  1.0]
        ])
        
        # Wait for controller to be ready
        print("Giving 8 seconds for controller to be switched on..")
        time.sleep(8.0)
        print("Setup complete. Ready for execution")

    def set_magnet(self, state: bool):
        """Control the magnet state."""
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect("/tmp/gpio_socket")
        sock.sendall(b"ON" if state else b"OFF")
        sock.close()

    def create_target_pose(self, x: float, y: float, z: float) -> np.ndarray:
        """Create a target pose matrix for the given coordinates."""
        if z > self.MAX_Z:
            raise ValueError(f"Z coordinate {z} exceeds maximum safe value of {self.MAX_Z}")
            
        return np.array([
            [1.0,  0.0,  0.0,  x],
            [0.0, -1.0,  0.0,  y],
            [0.0,  0.0, -1.0,  z],
            [0.0,  0.0,  0.0,  1.0]
        ])

    def wait_for_status(self, target_status: int, timeout: float = 30.0) -> bool:
        """Wait for a specific screw status value."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            current_status = self.franka.get_key_value("screw_status")
            if current_status == target_status:
                return True
            time.sleep(0.1)
        return False

    def apply_force_and_wait(self, force_duration: float, target_status: int, 
                           max_displacement: float = 0.1) -> bool:
        """Apply force and wait for displacement or timeout."""
        pose = self.franka.get_pose()
        initial_z = pose[2, 3]
        start_time = time.time()
        
        while time.time() - start_time < force_duration:
            pose = self.franka.get_pose()
            current_z = pose[2, 3]
            delta_z = abs(current_z - initial_z)
            
            if delta_z > max_displacement:
                self.franka.set_key_value("screw_status", target_status)
                return True
                
            time.sleep(0.05)
        
        self.franka.set_key_value("screw_status", target_status)
        return False

    def remove_screw(self, x: float, y: float, z: float) -> bool:
        """
        Remove a screw at the specified coordinates.
        
        Args:
            x: X coordinate of the screw
            y: Y coordinate of the screw
            z: Z coordinate of the screw
            
        Returns:
            bool: True if screw removal was successful, False otherwise
        """
        try:
            # Create target pose
            target_pose = self.create_target_pose(x, y, z)
            
            # Set initial status
            self.franka.set_key_value("screw_status", 0)
            
            # Wait for robot to reach home position
            if not self.wait_for_status(1):
                print("Failed to reach home position")
                return False
            
            # Move to target position
            print("\nMoving to target pose...")
            self.franka.move_to_pose(target_pose)
            time.sleep(1.0)
            
            # Start motor and activate magnet
            self.pwm_motor.set_duty_cycle_percent(8.4)
            self.set_magnet(True)
            time.sleep(0.5)
            
            # Set status for initial force application
            self.franka.set_key_value("screw_status", 2)
            
            # Apply initial force (1N)
            print("Applying 1 N..")
            if not self.apply_force_and_wait(3.0, 5):
                print("Initial force application failed")
                return False
            
            # Wait for desk loop completion
            if not self.wait_for_status(3):
                print("Desk loop failed after initial force")
                return False
            
            # Apply stronger force (5N)
            print("Applying 5 N..")
            self.pwm_motor.set_duty_cycle_percent(9.0)
            self.set_magnet(True)
            time.sleep(0.5)
            
            if not self.apply_force_and_wait(4.0, 6):
                print("Strong force application failed")
                return False
            
            # Wait for desk loop completion
            if not self.wait_for_status(4):
                print("Desk loop failed after strong force")
                return False
            
            # Wait for final status
            if not self.wait_for_status(7):
                print("Final status not reached")
                return False
            
            # Stop screwing
            self.pwm_motor.set_duty_cycle_percent(7.5)
            
            # Wait for removal confirmation
            if not self.wait_for_status(8):
                print("Removal confirmation not received")
                return False
            
            # Deactivate magnet and perform final rotation
            self.set_magnet(False)
            self.pwm_motor.set_duty_cycle_percent(9.0)
            time.sleep(0.2)
            self.pwm_motor.set_duty_cycle_percent(6.0)
            time.sleep(0.2)
            self.pwm_motor.set_duty_cycle_percent(7.5)
            
            return True
            
        except Exception as e:
            print(f"Error during screw removal: {str(e)}")
            return False

    def cleanup(self):
        """Clean up resources."""
        try:
            self.franka.disconnect()
            self.pwm_motor.set_duty_cycle_percent(7.5)
            self.pwm_motor.cleanup()
        except Exception as e:
            print(f"Error during cleanup: {str(e)}")

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully."""
    print("\nShutting down gracefully...")
    if 'robot' in globals():
        robot.cleanup()
    sys.exit(0)

if __name__ == "__main__":
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    # Create robot instance
    robot = MoveRobot()
    
    try:
        # Use the same coordinates as in unscrew_v02.py
        x_target = 0.5189
        y_target = 0.1511
        z_target = 0.12
        
        # Remove the screw
        success = robot.remove_screw(x_target, y_target, z_target)
        
        if success:
            print("Screw removal completed successfully!")
        else:
            print("Screw removal failed!")
            
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        robot.cleanup()