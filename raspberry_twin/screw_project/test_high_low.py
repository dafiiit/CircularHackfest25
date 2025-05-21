from hardware_interface.pwm import PWMChannel
import time

pwm_motor = PWMChannel(chip=0, channel=1, gpio_pin=12, frequency_hz=50)
pwm_motor.enable()

while True:
    pwm_motor.set_duty_cycle_percent(100)
    time.sleep(1.0)
    pwm_motor.set_duty_cycle_percent(0)
    time.sleep(1.0)