import os
from pynput.keyboard import Key, Listener

from stark.VICore import CommandsContext
from stark.VoiceAssistant import VoiceAssistant, Mode
from stark.IO.VoskSpeechRecognizer import VoskSpeechRecognizer
from stark.IO.SileroSpeechSynthesizer import SileroSpeechSynthesizer
from stark.features import default


cm = CommandsContext(commands_manager = default)
va = VoiceAssistant(
    speech_recognizer = VoskSpeechRecognizer(),
    speech_synthesizer = SileroSpeechSynthesizer(),
    commands_context = cm
)
va.mode = Mode(stop_after_interaction = True) # Wait for the hotkey to be pressed again

def on_release(key: Key):
    if key == Key.alt_r:
        '''
        optional: play a sound to indicate that the hotkey was pressed
        play all sounds in macos: sh`for s in /System/Library/Sounds/*; do echo "$s" && afplay "$s"; done`
        for linux: check the `/usr/share/sounds/` directory and use `aplay` instead of `afplay`
        
        as an alternative, you can use the a SpeechSynthesizer to say something like "Yes, sir?"
        '''
        os.system('afplay /System/Library/Sounds/Hero.aiff &') # play the sound in the background (macos)
        va.start()

listener = Listener(on_release = on_release)
listener.start()
