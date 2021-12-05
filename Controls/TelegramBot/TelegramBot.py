#!/usr/local/bin/python3.8

import time
import os
import config
from ArchieCore import Command, CommandsContext, CommandsContextDelegate
from General import Text2Speech
from ..Control import Control
from .MyTeleBot import MyTeleBot

class TelegramBot(Control, CommandsContextDelegate):
    threads = []
    online  = True
    voids   = 0
    memory  = []
    voice   = Text2Speech.Engine()
    bot     = MyTeleBot(config.telebot)
    commandsContext: CommandsContext

    # Control

    def __init__(self):
        self.commandsContext = CommandsContext(delegate = self)

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

    def main(self, id, text):
        self.commandsContext.processString(text.lower(), data = {'id': id})

    # CommandsContextDelegate

    def commandsContextDidReceiveResponse(self, response):
        id = response.data.get('id')
        if not id: return

        if response.text:
            self.bot.send_message(id, response.text)
        if response.voice:
            if bytes := self.voice.generate(response.voice).getBytes():
                self.bot.send_voice(id, bytes)

    # Telebot

    @bot.message_handler(commands=['vlc', 'queue', 'cmd'])
    def simple_commands(msg):
        command = msg.text.replace('/cmd', '').replace('/vlc', 'vlc')
        if '/queue' in msg.text: command = command.replace('/queue', '') + '--playlist-enqueue'
        os.system(f'lxterminal --command="{command}"')

    @bot.message_handler(commands=['terminal'])
    def terminal(msg):
        command = msg.text.replace('/terminal', '')
        output = os.popen(command).read()
        bot.send_message(msg.chat.id, output)

    @bot.message_handler(content_types = ['text'])
    def execute(msg):
        self.commandsContext.processString(msg.text.lower(), data = {'id': msg.chat.id})
