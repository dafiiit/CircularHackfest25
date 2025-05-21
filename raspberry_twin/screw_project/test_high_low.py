import socket
import time

def set_pin(state: bool):
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect("/tmp/gpio_socket")
    sock.sendall(b"ON" if state else b"OFF")
    sock.close()

# Usage:
try:
    while True:
        # Turn LED on
        set_pin(True)  # Turns pin HIGH
        time.sleep(1.0)  # LED on for 1 second
        # Turn LED off
        set_pin(False)  # Turns pin HIGH
        time.sleep(1.0)  # LED off for 1 second
        print("alive")
except KeyboardInterrupt:
    # Exit the loop on CTRL+C
    pass
finally:
    set_pin(False)  # Turns pin HIGH