import RPi.GPIO as GPIO
import socket

GPIO.setmode(GPIO.BCM)
LED_PIN = 4
GPIO.setup(LED_PIN, GPIO.OUT)

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
finally:
    sock.close()
    GPIO.cleanup()