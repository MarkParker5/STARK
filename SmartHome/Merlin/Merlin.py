from typing import List
from threading import Thread

try:
    import RPi.GPIO as GPIO
    import spidev
    GPIO.setmode(GPIO.BCM)
    is_rpi = True
except ModuleNotFoundError:
    is_rpi = False

from .MerlinMessage import MerlinMessage
from .lib_nrf24 import NRF24


class Merlin():
    radio: NRF24
    send_queue: List[MerlinMessage] = []
    my_urdi = [0xf0, 0xf0, 0xf0, 0xf0, 0xe1]

    def __init__(self):
        if not is_rpi: return

        radio = NRF24(GPIO, spidev.SpiDev())
        radio.begin(0, 17)
        radio.setPALevel(NRF24.PA_HIGH)
        radio.setDataRate(NRF24.BR_2MBPS)
        radio.setChannel(0x60)
        radio.setPayloadSize(2)
        radio.setAutoAck(True)
        #radio.setAddressWidth(4)
        radio.enableAckPayload()
        radio.openReadingPipe(1, self.my_urdi)

        radio.startListening()
        radio.stopListening()

        radio.startListening()

        self.radio = radio

    def send(self, message: MerlinMessage):
        self.send_queue.append(message)

    def _send(self, message: MerlinMessage):
        if not is_rpi:
            # TODO: Log
            print(message.urdi, message.data, [b.to_bytes(1, 'big') for b in message.data])
            return
        self.radio.stopListening()
        self.radio.openWritingPipe(message.urdi)
        self.radio.write(message.data)
        self.radio.startListening()

    def receiveAndTransmit(self):
        while True:
            # send messages from queue
            while self.send_queue and (message := self.send_queue.pop()):
                self._send(message)

            if not is_rpi: return

            # receiving messages
            if not self.radio.available():
                 continue

            rawData = []
            self.radio.read(rawData, self.radio.getPayloadSize())
            func, arg = rawData
            print(f'{func=} {arg=}') # TODO: Log

receiveAndTransmitThread = Thread(target = Merlin().receiveAndTransmit)
receiveAndTransmitThread.start()
