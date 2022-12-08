from abc import ABC

class Singleton(ABC):

    # Singleton
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super().__new__(cls)
        return cls.instance
