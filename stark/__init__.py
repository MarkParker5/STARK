import asyncer

from stark.interfaces.protocols import (
    SpeechRecognizer,
    SpeechRecognizerDelegate,
    SpeechSynthesizer,
    SpeechSynthesizerResult
)   
from stark.core import (
    Command,
    Pattern,
    Response,
    ResponseStatus,
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
    speech_recognizer: SpeechRecognizer,
    speech_synthesizer: SpeechSynthesizer
):
    async with asyncer.create_task_group() as main_task_group:
        context = CommandsContext(
            task_group = main_task_group, 
            commands_manager = manager
        )
        voice_assistant = VoiceAssistant(
            speech_recognizer = speech_recognizer,
            speech_synthesizer = speech_synthesizer,
            commands_context = context
        )
        speech_recognizer.delegate = voice_assistant
        context.delegate = voice_assistant
        
        main_task_group.soonify(speech_recognizer.start_listening)()
        main_task_group.soonify(context.handle_responses)()
        
        detector = BlockageDetector()
        main_task_group.soonify(detector.monitor)()
