import contextlib
import asyncer

from stark.interfaces.protocols import (
    SpeechRecognizer,
    SpeechRecognizerDelegate,
    SpeechSynthesizer,
    SpeechSynthesizerResult
)
from stark.interfaces.recognizer_relay import SpeechRecognizerRelay
from stark.interfaces.microphone import Microphone
from stark.core import (
    Command,
    Pattern,
    Response,
    ResponseHandler,
    AsyncResponseHandler,
    CommandsContext,
    CommandsManager
)
from stark.voice_assistant import (
    VoiceAssistant,
    Mode
)
from stark.general.blockage_detector import BlockageDetector


async def run(
    manager: CommandsManager,
    speech_recognizers: list[SpeechRecognizer],
    speech_synthesizer: SpeechSynthesizer
):
    async with run_task_group(
        manager = manager,
        speech_recognizers = speech_recognizers,
        speech_synthesizer = speech_synthesizer
    ): pass
    
@contextlib.asynccontextmanager
async def run_task_group(
    manager: CommandsManager,
    speech_recognizers: list[SpeechRecognizer],
    speech_synthesizer: SpeechSynthesizer
):
    async with asyncer.create_task_group() as main_task_group:
        
        relay = SpeechRecognizerRelay(speech_recognizers)
        
        context = CommandsContext(
            task_group = main_task_group, 
            commands_manager = manager
        )
        
        voice_assistant = VoiceAssistant(
            speech_recognizer = relay,
            speech_synthesizer = speech_synthesizer,
            commands_context = context
        )
        
        # Set delegates
        
        relay.delegate = voice_assistant
        context.delegate = voice_assistant
        
        # Start main tasks
        
        relay.start_speech_recognizers(main_task_group)
        main_task_group.soonify(context.handle_responses)()
        
        # Microphone
                
        microphone = Microphone(relay.microphone_did_receive_sample)
        main_task_group.soonify(microphone.start_listening)()
        
        # Blockage Detector
        
        detector = BlockageDetector()
        main_task_group.soonify(detector.monitor)()
        
        # Yield main task group to allow to add tasks from outside
        
        yield main_task_group
