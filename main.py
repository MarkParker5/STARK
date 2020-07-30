import SpeechRecognition
import Text2Speech
import SmallTalk
from Command import Command
import config

listener = SpeechRecognition.SpeechToText()
voice    = Text2Speech.Engine()
threads  = []
memory   = []
online   = False
voids    = 0
listener.listen_noise()

def check_threads():
    for thread in threads:
        if thread['finish_event'].is_set():
            responce = thread['thread'].join()
            if responce['text']:
                print(' — '+responce['text'])
            if responce['voice']:
                voice.generate(responce['voice']).speak()
            thread['finish_event'].clear()
            del thread

while True:                     #    main loop
    check_threads()
    print('\nYou: ', end='')
    speech = listener.listen()
    text   = speech['text']
    if speech['status'] == 'ok':
        print(text)
        if online := set(config.names) & set(text.split(' ')):
            voids = 0
            cmd, params = Command.reg_find(text).values()
            responce = cmd.start(params)
            memory.insert(0, {
                'text': text,
                'cmd':  cmd,
                'responce': responce
            })
            if responce['type'] == 'background':        #   add background thread to list
                threads.append(responce['thread'])
            if responce['text']:
                print('Archie: '+responce['text'])
            if responce['voice']:
                voice.generate(responce['voice']).speak()
    else:
        if speech['status'] == 'error': print('Отсутсвует подключение к интернету');
        elif online and speech['status']  == 'void': voids += 1;
        if online and voids >= 3: online = False; voids = 0
        if not online: listener.listen_noise()
