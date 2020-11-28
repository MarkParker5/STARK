from Command import Command                     #   import parent class

class Raspi(Command):
    def start(this, string):                    #   main method
        pass

    def hdmi_cec(this, command):
        os.system(f'echo \'{command}\' | cec-client -s -d 1')
