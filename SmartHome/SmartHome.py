import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
from lib_nrf24 import NRF24
import spidev

import time
import json as JSON
from Command import Command
from threading import Thread

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

    def start(this, string):                    #   main method
        pass

    @staticmethod
    def send(data):
        SmartHome.send_queue.append(data)

    @staticmethod
    def _send(data):
        while radioIsBusy: tile.sleep(0.1)
        string = JSON.dumps(data)
        for char in string: radio.write(char)

    @staticmethod
    def receiveAndTransmit():
        json = ''
        while True:
            for command in SmartHome.send_queue: _send(command)
            #   listening radio
            while not radio.available(): time.sleep(0.01)
            recv_buffer = []
            radio.read(recv_buffer, radio.getDynamicPayloadSize())
            if recv_buffer[0] != 10:
                json += chr(recv_buffer[0])
                continue
            print(json)
            #   parsing of received data
            data = JSON.loads(json)
            if name := data.get('name'):
                params = data.get('params') or {}
                if cmd := Command.getCommand(name):
                    try: cmd.start(params)
                    except: pass
            json = ''

receiveAndTransmitThread = Thread(target=SmartHome.receiveAndTransmit)
receiveAndTransmitThread.start()
