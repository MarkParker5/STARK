from abc import ABC, abstractmethod

class Control(ABC):

    @abstractmethod
    def start(self):
        # entry point of the control
        pass
