from abc import ABC, abstractmethod
from General import Singleton

class Control(Singleton):

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass
