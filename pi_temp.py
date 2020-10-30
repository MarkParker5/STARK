import os
import time
import RPi.GPIO as GPIO

pin = 3

def current_temp():
    temp = os.popen("vcgencmd measure_temp").readline()
    return temp.replace("temp=","")

GPIO.setup(pin, GPIO.OUT)
while True:
    temp = int(current_temp())
    if temp > 55:
        cooling = True
    elif temp < 40:
        cooling = False
    GPIO.output(pin, cooling)
    print(f'temp={temp}, cooling={cooling}')
    time.sleep(1)
