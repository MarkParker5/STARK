#!/usr/local/bin/python3.8

import time
import os
import telebot
import config
from Features import Command
from General import Text2Speech
from Controls.Control import Control

class TelegramBot(Control):
    threads = []
    online  = True
    voids   = 0
    memory  = []
    voice   = Text2Speech.Engine()
    bot     = telebot.TeleBot(config.telebot)

    #   Singleton
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(TelegramBot, cls).__new__(cls)
        return cls.instance

    def reply(self, id, response):
        if response.text:
            bot.send_message(id, response.text)
        if response.voice:
            bot.send_voice(id, voice.generate(response.voice).getBytes() )
        if response.thread:                        #   add background thread to list
            response.thread['id'] = id
            threads.append(response.thread)

    def check_threads(self, threads):
        for thread in threads:
            if thread['finish_event'].is_set():
                response = thread['thread'].join()
                reply(thread['id'], response)
                thread['finish_event'].clear()
                del thread

    def main(self, id, text):
        text = text.lower()
        if Command.isRepeat(text):
            reply(id, memory[0]['response']);
            return
        if memory:
            response = memory[0]['response']
            if response.callback:
                if new_response := response.callback.answer(text):
                    reply(id, new_response)
                    memory.insert(0, {
                        'cmd':  response.callback,
                        'params': None,
                        'response': new_response,
                    })
                    return
        try:
            cmd, params = memory[0]['cmd'].checkContext(text).values()
            if memory[0].get('params'): params = {**memory[0].get('params'), **params}
        except:
            cmd, params = Command.reg_find(text).values()
        response = cmd.start(params)
        reply(id, response)
        memory.insert(0, {
            'cmd':  cmd,
            'params': params,
            'response': response,
        })

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
        main(msg.chat.id, msg.text)

    def start(self):
        while True:
            try:
                print("Start polling...")
                bot.polling(callback = check_threads, args = (threads,) )
            except Exception as e:
                print(e, "\nPolling failed")
                time.sleep(10)


if __name__ == '__main__':
    TelegramBot().start()
