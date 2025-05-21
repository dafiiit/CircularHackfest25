import json
import socket

DAEMON_SOCKET_PATH = '/var/run/pwm_daemon.sock'

def send_command(command: dict) -> dict:
    """Helper to send a command to the PWM daemon and return the parsed JSON response."""
    try:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(DAEMON_SOCKET_PATH)
        sock.sendall(json.dumps(command).encode('utf-8'))
        response = sock.recv(1024).decode('utf-8')
        sock.close()
        return json.loads(response)
    except Exception as e:
        return {"status": "error", "message": str(e)}

class PWMChannel:
    """
    Proxy class for controlling PWM channels via a privileged daemon.
    This class sends commands over a Unix domain socket to the PWM daemon,
    which performs the hardware-level operations.
    """
    def __init__(self, chip: int, channel: int, gpio_pin: int, frequency_hz: float):
        self.chip = chip
        self.channel = channel
        self.gpio_pin = gpio_pin
        self.frequency_hz = frequency_hz

        # Send a "create" command to initialize the PWM channel.
        command = {
            "action": "create",
            "chip": self.chip,
            "channel": self.channel,
            "gpio_pin": self.gpio_pin,
            "frequency_hz": self.frequency_hz
        }
        response = send_command(command)
        if response.get("status") == "ok":
            print(f"[Client] PWM channel {self.chip}:{self.channel} created successfully.")
        else:
            print(f"[Client] Error creating PWM channel: {response.get('message')}")

    def enable(self):
        command = {
            "action": "enable",
            "chip": self.chip,
            "channel": self.channel
        }
        response = send_command(command)
        if response.get("status") != "ok":
            print(f"[Client] Error enabling PWM: {response.get('message')}")

    def disable(self):
        command = {
            "action": "disable",
            "chip": self.chip,
            "channel": self.channel
        }
        response = send_command(command)
        if response.get("status") != "ok":
            print(f"[Client] Error disabling PWM: {response.get('message')}")

    def set_duty_cycle_percent(self, percent: float):
        command = {
            "action": "set_duty",
            "chip": self.chip,
            "channel": self.channel,
            "value": percent
        }
        response = send_command(command)
        if response.get("status") != "ok":
            print(f"[Client] Error setting duty cycle: {response.get('message')}")

    def cleanup(self):
        command = {
            "action": "cleanup",
            "chip": self.chip,
            "channel": self.channel
        }
        response = send_command(command)
        if response.get("status") != "ok":
            print(f"[Client] Error cleaning up PWM: {response.get('message')}")
