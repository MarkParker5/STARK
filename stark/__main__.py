import anyio
import asyncer

from stark.core import CommandsContext, CommandsManager, Response
from stark.interfaces.silero import SileroSpeechSynthesizer
from stark.interfaces.vosk import VoskSpeechRecognizer
from stark.voice_assistant import VoiceAssistant
# from stark.types import Number, String
import config


manager = CommandsManager()

@manager.new('привет')
def hello_world():
    return Response(
        text = 'Привет, мир!', 
        voice = 'Привет, мир!'
    )
    
@manager.new('пока')
async def by_world():
    return Response(
        text = 'Прощай, мир!', 
        voice = 'Прощай, мир!'
    )

async def main(): # manager: CommandsManager, speech_recognizer: SpeechRecognizer, speech_synthesizer: SpeechSynthesizer):
    async with asyncer.create_task_group() as main_task_group:
        sr = VoskSpeechRecognizer(
            vosk_model_path = config.vosk_model
        )
        stt = SileroSpeechSynthesizer(
            model_url = config.silero_model_url   
        )
        cc = CommandsContext(
            task_group = main_task_group, 
            commands_manager = manager
        )
        va = VoiceAssistant(
            speech_recognizer = sr,
            speech_synthesizer = stt,
            commands_context = cc
        )
        sr.delegate = va
        cc.delegate = va
        
        main_task_group.soonify(sr.start_listening)()
        main_task_group.soonify(cc.handle_responses)()

if __name__ == '__main__':
    anyio.run(main)
