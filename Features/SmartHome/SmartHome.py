import RPi.GPIO as GPIO
from .lib_nrf24 import NRF24
import spidev

import time
import json as JSON
from threading import Thread
from ArchieCore import Command

GPIO.setmode(GPIO.BCM)

pipe = [0xf0, 0xf0, 0xf0, 0xf0, 0xe1]

radio = NRF24(GPIO, spidev.SpiDev())
radio.begin(0, 17)
radio.setRetries(15,15)
radio.setPayloadSize(32)
radio.setChannel(0x60)
radio.setDataRate(NRF24.BR_250KBPS)
radio.setPALevel(NRF24.PA_HIGH)
radio.setAutoAck(True)
radio.enableDynamicPayloads()
radio.enableAckPayload()
radio.openWritingPipe(pipe)
radio.openReadingPipe(1, pipe)

radio.startListening()
radio.stopListening()

radio.startListening()

class SmartHome(Command):
    radio = radio
    send_queue = []

    def start(self, string):                    #   main method
        pass

    @staticmethod
    def send(data):
        SmartHome.send_queue.append(data)

    @staticmethod
    def _send():
        data = SmartHome.send_queue.pop()
        print(data)
        string = JSON.dumps(data)
        for char in string: radio.write(char)

    @staticmethod
    def receiveAndTransmit():
        json = ''
        while True:
            if SmartHome.send_queue:
                radio.stopListening()
                while SmartHome.send_queue: SmartHome._send()
                radio.startListening()

            #   listening radio
            if not radio.available(): continue
            recv_buffer = []
            radio.read(recv_buffer, radio.getDynamicPayloadSize())
            char = chr(recv_buffer[0])

            if char == '{':
                json = '{'
                continue
            else if char == '}':
                json += char
                print(json)
            else if char in ['\n', ';']:
                continue
            else:
                json += char
                continue

            #   parsing of received data
            try: data = JSON.loads(json)
            except: data = {}
            if data.get('target') != 'hub':
                json = ''
                continue
            if name := data.get('cmd'):
                params = data.get('params') or {}
                if cmd := Command.getCommand(name):
                    try: cmd.start(params)
                    except: pass
            json = ''

receiveAndTransmitThread = Thread(target=SmartHome.receiveAndTransmit)
receiveAndTransmitThread.start()
