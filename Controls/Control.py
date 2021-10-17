from abc import ABC, abstractmethod

class Control(ABC):
    
    # Singleton
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super().__new__(cls)
        return cls.instance

    @abstractmethod
    def start(self):
        # entry point of the control
        pass
