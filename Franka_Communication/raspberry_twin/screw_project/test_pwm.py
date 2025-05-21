from hardware_interface.pwm import PWMChannel
import time

pwm_motor = PWMChannel(chip=0, channel=1, gpio_pin=13, frequency_hz=50)
pwm_motor.enable()

pwm_motor.set_duty_cycle_percent(7.5)
time.sleep(10.0)

while True:
    pwm_motor.set_duty_cycle_percent(7.5)
    time.sleep(1.0)
    pwm_motor.set_duty_cycle_percent(9.0)
    time.sleep(1.0)
    pwm_motor.set_duty_cycle_percent(7.5)
    time.sleep(1.0)
    pwm_motor.set_duty_cycle_percent(6.0)
    time.sleep(1.0)