import contextlib
import asyncer

from stark.interfaces.protocols import (
    SpeechRecognizer,
    SpeechRecognizerDelegate,
    SpeechSynthesizer,
    SpeechSynthesizerResult
)
from stark.interfaces.recognizer_relay import RecognizerRelay
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
        context = CommandsContext(
            task_group = main_task_group, 
            commands_manager = manager
        )
        voice_assistant = VoiceAssistant(
            speech_recognizer = speech_recognizers[0], # TODO: list or callbacks
            speech_synthesizer = speech_synthesizer,
            commands_context = context
        )
        
        context.delegate = voice_assistant
        main_task_group.soonify(context.handle_responses)()
        
        # Speech Recognition
        
        relay = RecognizerRelay()
        # relay.delegate = voice_assistant # TODO: implement
        
        def microphone_callback(data):
            for recognizer in speech_recognizers:
                recognizer.microphone_did_receive_sample(data)
                
        microphone = Microphone(microphone_callback)
        
        main_task_group.soonify(microphone.start_listening)()
        for recognizer in speech_recognizers:    
            recognizer.delegate = relay
            main_task_group.soonify(recognizer.start_listening)()
        
        # Blockage Detector
        
        detector = BlockageDetector()
        main_task_group.soonify(detector.monitor)()
        
        yield main_task_group
