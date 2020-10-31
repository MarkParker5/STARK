import os
import time
import RPi.GPIO as GPIO

pin = 3
cooling = False

def current_temp():
    temp = os.popen("vcgencmd measure_temp").readline()
    return temp.replace("temp=","")

GPIO.setmode(GPIO.BCM)
GPIO.setup(pin, GPIO.OUT)
while True:
    temp = float(current_temp()[:4])
    if temp > 55:
        cooling = True
    elif temp < 40:
        cooling = False
    GPIO.output(pin, cooling)
    print(f'temp={temp}, cooling={cooling}')
    time.sleep(1)
