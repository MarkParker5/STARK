import asyncer

from stark.core import (
    Command,
    CommandsContext,
    CommandsManager,
    Pattern,
    Response,
    ResponseStatus,
)
from stark.core.commands_context_processor import CommandsContextProcessor
from stark.core.health_check import health_check
from stark.core.processors.search_processor import SearchProcessor
from stark.general.blockage_detector import BlockageDetector
from stark.interfaces.protocols import (
    SpeechRecognizer,
    SpeechRecognizerDelegate,
    SpeechSynthesizer,
    SpeechSynthesizerResult,
)
from stark.voice_assistant import Mode, VoiceAssistant


async def run(
    manager: CommandsManager,
    speech_recognizer: SpeechRecognizer,
    speech_synthesizer: SpeechSynthesizer,
    processors: list[CommandsContextProcessor] = [SearchProcessor()],
):
    async with asyncer.create_task_group() as main_task_group:
        context = CommandsContext(
            task_group=main_task_group,
            commands_manager=manager,
            processors=processors,
        )
        voice_assistant = VoiceAssistant(
            speech_recognizer=speech_recognizer,
            speech_synthesizer=speech_synthesizer,
            commands_context=context,
        )
        speech_recognizer.delegate = voice_assistant
        context.delegate = voice_assistant

        health_check(context.pattern_parser, manager.commands)

        main_task_group.soonify(speech_recognizer.start_listening)()
        main_task_group.soonify(context.handle_responses)()

        detector = BlockageDetector()
        main_task_group.soonify(detector.monitor)()
