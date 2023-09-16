import anyio
import asyncer

from stark.core import CommandsContext, CommandsManager, Response
from stark.interfaces.silero import SileroSpeechSynthesizer
from stark.interfaces.vosk import VoskSpeechRecognizer
from stark.voice_assistant import VoiceAssistant
from stark.general.blockage_detector import BlockageDetector
# from stark.types import Number, String
import config


manager = CommandsManager()

@manager.new('привет')
def hello_world():
    return Response(
        text = 'Hello 10 times', 
        voice = 'Привет, мир!, Привет, мир!, Привет, мир!, Привет, мир!, Привет, мир!, Привет, мир!, Привет, мир!, Привет, мир!, Привет, мир!, Привет, мир!, Привет, мир!'
    )
    
@manager.new('пока')
async def by_world():
    import time
    time.sleep(1.5) # simulate blocking operation
    return Response(
        text = 'Прощай, мир!', 
        voice = 'Прощай, мир!'
    )
    
@manager.new('фоновый режим')
def by_world_sync_bg():
    import time
    time.sleep(6) # simulate blocking operation
    return Response(
        text = 'Прощай, мир!', 
        voice = 'Прощай, мир!'
    )

async def main(): # manager: CommandsManager, speech_recognizer: SpeechRecognizer, speech_synthesizer: SpeechSynthesizer):
    async with asyncer.create_task_group() as main_task_group:
        
        sr = VoskSpeechRecognizer(
            model_url = config.vosk_model_url
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
        
        detector = BlockageDetector(threshold = 1)
        main_task_group.soonify(detector.monitor)()

if __name__ == '__main__':
    anyio.run(main)
