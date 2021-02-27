#!/usr/local/bin/python3.8
from Command import Command
import SpeechRecognition
import Text2Speech
import telebot
import config
import modules
import time

threads = []
online  = True
voids   = 0
memory  = []
voice   = Text2Speech.Engine()
listener= SpeechRecognition.SpeechToText()
bot     = telebot.TeleBot(config.telebot)

def reply(id, response):
    if response.text:
        bot.send_message(id, response.text)
    if response.voice:
        bot.send_voice(id, voice.generate(response.voice).getBytes() )
    if response.thread:                        #   add background thread to list
        response.thread['id'] = id
        threads.append(response.thread)


def check_threads(threads):
    for thread in threads:
        if thread['finish_event'].is_set():
            response = thread['thread'].join()
            reply(thread['id'], response)
            thread['finish_event'].clear()
            del thread

def main(id, text):
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

@bot.message_handler(content_types = ['text'])
def execute(msg):
    main(msg.chat.id, msg.text)


while True:
    try:
        print("Start polling...")
        bot.polling(callback = check_threads, args = (threads,) )
    except:
        time.sleep(10)
        print("Polling failed")
