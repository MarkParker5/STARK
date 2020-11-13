from Command import Command                     #   import parent class
import time

# for nrf24l01
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
from lib_nrf24 import NRF24
import spidev

radio = NRF24(GPIO, spidev.SpiDev())
radio.begin(0, 17)
time.sleep(1)
radio.setRetries(15,15)
radio.setPayloadSize(32)
radio.setChannel(0x60)

radio.setDataRate(NRF24.BR_250KBPS)
radio.setPALevel(NRF24.PA_HIGH)
radio.setAutoAck(True)
radio.enableDynamicPayloads()
radio.enableAckPayload()

radio.openWritingPipe([0xf0, 0xf0, 0xf0, 0xf0, 0xe1])

class SmartHome(Command):
    radio = radio
    def start(this, string):                    #   main method
        pass

    @staticmethod
    def send(data):
        string = '{'
        for key, value in data.items():
            string += f'"{key}": "{value}", '
        string += '}\n'
        for char in data:
            radio.write(char)
