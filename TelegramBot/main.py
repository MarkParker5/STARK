import os, sys

# root = os.path.dirname(os.path.dirname(__file__))
# sys.path.append(root)
# sys.path.append(root + '/VoiceAssistant')

from TelegramBot import TelegramBot


if __name__ == '__main__':
    TelegramBot().start()
