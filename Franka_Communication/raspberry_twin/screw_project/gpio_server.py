import RPi.GPIO as GPIO
import socket
import os
import signal
import sys

# Cleanup handler
def cleanup(signum=None, frame=None):
    try:
        if 'sock' in globals():
            sock.close()
        if os.path.exists("/tmp/gpio_socket"):
            os.unlink("/tmp/gpio_socket")
    finally:
        GPIO.cleanup()
        sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

GPIO.setmode(GPIO.BCM)
LED_PIN = 4
GPIO.setup(LED_PIN, GPIO.OUT)

# Ensure socket doesn't exist from previous run
if os.path.exists("/tmp/gpio_socket"):
    os.unlink("/tmp/gpio_socket")

sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
sock.bind("/tmp/gpio_socket")
sock.listen(1)

try:
    while True:
        conn, _ = sock.accept()
        cmd = conn.recv(3).decode()
        if cmd == "ON":
            GPIO.output(LED_PIN, True)
        elif cmd == "OFF":
            GPIO.output(LED_PIN, False)
        conn.close()
except Exception as e:
    print(f"Error: {e}")
    cleanup()