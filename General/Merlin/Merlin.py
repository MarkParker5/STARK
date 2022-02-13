import RPi.GPIO as GPIO
from .lib_nrf24 import NRF24
import spidev

from threading import Thread
from ArchieCore import Command
from .MerlinMessage import MerlinMessage

GPIO.setmode(GPIO.BCM)

class Merlin():
    radio: NRF24
    send_queue: List[MerlinMessage] = []

    def __init__(self):
        pipe = [0xf0, 0xf0, 0xf0, 0xf0, 0xe1]

        radio = NRF24(GPIO, spidev.SpiDev())
        radio.begin(0, 17)
        radio.setPALevel(NRF24.PA_HIGH)
        radio.setDataRate(NRF24.BR_2MBPS)
        radio.setChannel(0x60)
        radio.setPayloadSize(8)
        radio.setAutoAck(False)
        # radio.openWritingPipe(pipe)
        radio.openReadingPipe(1, pipe)

        radio.startListening()
        radio.stopListening()

        radio.startListening()

        self.radio = radio

    def send(self, data):
        self.send_queue.append(data)

    def _send(self, message: MerlinMessage):
        self.radio.stopListening()
        self.radio.write(message.rawData)
        self.radio.startListening()

    def receiveAndTransmit(self):
        while True:
            # send messages from queue
            while self.send_queue and (message := self.send_queue.pop()):
                self._send(message)

            # receiving messages
            if not self.radio.available():
                 continue

            rawData = []
            self.radio.read(rawData, self.radio.getPayloadSize())
            message = MerlinMessage.parseRaw(rawData)
            print(f'{message.urdi=} {message.func=} {message.arg=}')

receiveAndTransmitThread = Thread(target=Merlin().receiveAndTransmit)
receiveAndTransmitThread.start()
