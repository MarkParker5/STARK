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
from stark.general.localisation import Localizer
from stark.interfaces.protocols import (
    SpeechRecognizer,
    SpeechRecognizerDelegate,
    SpeechSynthesizer,
    SpeechSynthesizerResult,
)
from stark.voice_assistant import Mode, VoiceAssistant


async def run(
    manager: CommandsManager,
    speech_recognizer: SpeechRecognizer | list[SpeechRecognizer],
    speech_synthesizer: SpeechSynthesizer,
    processors: list[CommandsContextProcessor] | None = None,
    localizer: Localizer | None = None,
):
    if processors is None:
        processors = [SearchProcessor()]

    async with asyncer.create_task_group() as main_task_group:
        context = CommandsContext(
            task_group=main_task_group,
            commands_manager=manager,
            processors=processors,
            localizer=localizer,
        )

        from stark.interfaces.microphone import Microphone

        recognizers = speech_recognizer if isinstance(speech_recognizer, list) else [speech_recognizer]
        use_relay = len(recognizers) > 1

        if use_relay:
            from stark.interfaces.recognizer_relay import SpeechRecognizerRelay
            effective_recognizer = SpeechRecognizerRelay(recognizers)
        else:
            effective_recognizer = recognizers[0]

        voice_assistant = VoiceAssistant(
            speech_recognizer=effective_recognizer,
            speech_synthesizer=speech_synthesizer,
            commands_context=context,
        )
        effective_recognizer.delegate = voice_assistant
        context.delegate = voice_assistant

        health_check(context.pattern_parser, manager.commands)

        if use_relay:
            effective_recognizer.start_speech_recognizers(main_task_group)
        else:
            main_task_group.soonify(effective_recognizer.start_listening)()

        microphone = Microphone(effective_recognizer.microphone_did_receive_sample)
        main_task_group.soonify(microphone.start_listening)()

        main_task_group.soonify(context.handle_responses)()

        detector = BlockageDetector()
        main_task_group.soonify(detector.monitor)()
