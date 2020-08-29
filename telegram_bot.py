from Command import Command
import SpeechRecognition
import Text2Speech
import SmallTalk
import telebot
import config
import QA

threads = []
online  = True
voids   = 0
memory  = []
voice   = Text2Speech.Engine()
listener= SpeechRecognition.SpeechToText()
bot     = telebot.TeleBot(config.telebot)

def reply(id, responce):
    if responce['text']:
        bot.send_message(id, responce['text'])
    if responce['voice']:
        bot.send_voice(id, voice.generate(responce['voice']).getBytes() )

def check_threads(threads):
    for thread in threads:
        if thread['finish_event'].is_set():
            responce = thread['thread'].join()
            reply(thread['id'], responce)
            thread['finish_event'].clear()
            del thread

def main(id, text):
    text = text.lower()
    if Command.isRepeat(text):
        reply(memory[0]['responce']);
        return
    try:    cmd, params = memory[0]['cmd'].checkContext(text).values(); params = {**memory[0]['params'], **params}
    except: cmd, params = Command.reg_find(text).values()
    responce = cmd.start(params)
    reply(id, responce)
    if responce['type'] == 'background':                        #   add background thread to list
        responce['thread']['id'] = id
        threads.append(responce['thread'])
    memory.insert(0, {
        'cmd':  cmd,
        'params': params,
        'responce': responce,
    })

@bot.message_handler(content_types = ['text'])
def execute(msg):
    main(msg.chat.id, msg.text)


while True:
    #try:
        print("Start polling...")
        bot.polling(callback = check_threads, args = (threads,) )
    #except:
        print("Polling failed")
