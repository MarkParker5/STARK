import SpeechRecognition
import Text2Speech
import SmallTalk
from Command import Command

listener = SpeechRecognition.SpeechToText()
voice    = Text2Speech.Engine()
threads  = []
memory   = []
listener.listen_noise()

def check_threads():
    for thread in threads:
        if thread['finish_event'].is_set():
            responce = thread['thread'].join()
            if responce['text']:
                voice.generate(responce['text']).speak()
            thread['finish_event'].clear()
            del thread

while True:                     #    main loop
    check_threads()
    print('Listening...')
    speech = listener.listen()
    text   = speech['text']
    print('You: ')
    if text:
        cmd      = Command.find(text)
        responce = cmd.start(text)
        memory.insert(0, {
            'text': text,
            'cmd':  cmd,
            'responce': responce
        })
        if responce['type'] == 'background':        #   add background thread to list
            threads.append(responce['thread'])
        if responce['text']:
            voice.generate(responce['text']).speak()
    else:
        print(speech['status'])
