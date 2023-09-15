import anyio
import asyncer

from stark import voice_assistant
from stark.core import CommandsContext, CommandsManager, Command
from stark.interfaces.silero import SileroSpeechSynthesizer
from stark.interfaces.vosk import VoskSpeechRecognizer
# from stark.types import Number, String


manager = CommandsManager()

@manager.new('hello')
def hello_world():
    return 'Hello, world!'

async def main(): # manager: CommandsManager, speech_recognizer: SpeechRecognizer, speech_synthesizer: SpeechSynthesizer):
    async with asyncer.create_task_group() as main_task_group:
        sr = VoskSpeechRecognizer()
        cc = CommandsContext(
            task_group = main_task_group, 
            commands_manager = manager
        )
        va = voice_assistant(
            speech_synthesizer = SileroSpeechSynthesizer(),
            commands_context = cc
        )
        sr.delegate = va
        
        main_task_group.soonify(sr.start_listening)()
        main_task_group.soonify(cc.handle_responses)()

if __name__ == '__main__':
    anyio.run(main)
