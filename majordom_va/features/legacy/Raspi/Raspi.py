import os

class Raspi():
    @staticmethod
    def hdmi_cec(command):
        os.system(f'echo \'{command}\' | cec-client -s -d 1')
