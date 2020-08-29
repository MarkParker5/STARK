import SpeechRecognition
import Text2Speech
import SmallTalk
from Command import Command
import config
import QA

listener = SpeechRecognition.SpeechToText()
voice    = Text2Speech.Engine()
threads  = []
memory   = []
online   = True
voids    = 0
listener.listen_noise()

def reply(responce):
    if responce['text']:                                #   print answer
        print('Archie: '+responce['text'])
    if responce['voice']:                               #   say answer
        voice.generate(responce['voice']).speak()
    if responce['type'] == 'background':                #   add background thread to list
        threads.append(responce['thread'])

def check_threads():
    for thread in threads:
        if thread['finish_event'].is_set():
            responce = thread['thread'].join()
            reply(responce)
            thread['finish_event'].clear()
            del thread

while True:                     #    main loop
    check_threads()
    print('\nYou: ', end='')
    speech = listener.listen()
    text   = speech['text']
    if speech['status'] == 'ok':
        print(text)
        voids = 0
        if name := list(set(config.names) & set(text.split(' '))):
            online = True
            text   = text.replace(name[0], '').strip()
        if online:
            if Command.isRepeat(text):
                reply(memory[0]['responce']);
                continue
            try: cmd, params = memory[0]['cmd'].checkContext(text).values(); params = {**memory[0]['params'], **params}
            except: cmd, params = Command.reg_find(text).values()
            responce = cmd.start(params)
            reply(responce)
            memory.insert(0, {
                'text': text,
                'cmd':  cmd,
                'responce': responce
            })
    else:
        if speech['status'] == 'error': print('Отсутсвует подключение к интернету');
        elif online and speech['status']  == 'void': voids += 1;
        if online and voids >= 3: online = False; voids = 0
        if not online: listener.listen_noise()
