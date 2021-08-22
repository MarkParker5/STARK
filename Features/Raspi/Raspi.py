from ..Command import Command                     #   import parent class
import os

class Raspi(Command):
    def start(this, string):                    #   main method
        pass

    @staticmethod
    def hdmi_cec(command):
        os.system(f'echo \'{command}\' | cec-client -s -d 1')
