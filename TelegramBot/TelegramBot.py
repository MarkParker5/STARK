import time
import os

import config
from ArchieCore import Command, CommandsContextManager, CommandsContextManagerDelegate
from IO import Text2Speech
from Features.Media import YoutubePlayer, TorrentPlayer
from CallbackTeleBot import CallbackTeleBot


class TelegramBot(CommandsContextManagerDelegate):

    online  = True
    voids   = 0
    voice   = Text2Speech.Engine()
    bot     = CallbackTeleBot(config.telebot)
    commandsContext: CommandsContextManager

    # Control

    def __init__(self):
        self.commandsContext = CommandsContextManager(delegate = self)

    def start(self):
        while True:
            try:
                print("Start polling...")
                self.bot.polling(callback = self.commandsContext.checkThreads)
            except Exception as e:
                print(e, "\nPolling failed")
                time.sleep(10)

    def stop(self):
        raise NotImplementedError

    # CommandsContextManagerDelegate

    def commandsContextDidReceiveResponse(self, response):
        id = response.data.get('id')
        if not id: return

        if response.text:
            self.bot.send_message(id, response.text)
        if response.voice:
            path = self.voice.generate(response.voice).path
            voiceFile = open(path, 'rb')
            try:
                self.bot.send_voice(id, voiceFile)
            finally:
                voiceFile.close()

    # Telebot

    @bot.message_handler(commands = ['vlc', 'queue', 'cmd'])
    def simple_commands(msg):
        command = msg.text.replace('/cmd', '').replace('/vlc', 'vlc')
        if '/queue' in msg.text: command = 'vlc ' + command.replace('/queue', '') + '--playlist-enqueue'
        os.system(f'lxterminal --command="{command}"')

    @bot.message_handler(commands=['terminal'])
    def terminal(msg):
        command = msg.text.replace('/terminal', '')
        output = os.popen(command).read()
        bot.send_message(msg.chat.id, output)

    @bot.message_handler(content_types = ['text'])
    def execute(msg):
        if 'youtu' in msg.text:
            YoutubePlayer(msg.text).play()
        elif '.torrent' in msg.text:
            TorrentPlayer.playUrl(msg.text)
        else:
            TelegramBot().commandsContext.processString(msg.text.lower(), data = {'id': msg.chat.id})
