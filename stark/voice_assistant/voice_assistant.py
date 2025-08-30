import logging
import os
from datetime import datetime
from typing import cast

logger = logging.getLogger(__name__)

from ..core import (
    CommandsContext,
    CommandsContextDelegate,
    CommandsContextLayer,
    Pattern,
    Response,
    ResponseStatus,
)
from ..interfaces.protocols import (
    SpeechRecognizer,
    SpeechRecognizerDelegate,
    SpeechSynthesizer,
)
from .mode import Mode


class ResponseCache(Response):
    # needs to save timeout_before_repeat that was set by mode at the moment of saving because it can change later and may lead to skipping responses
    timeout_before_repeat: int = 0

class VoiceAssistant(SpeechRecognizerDelegate, CommandsContextDelegate):

    speech_recognizer: SpeechRecognizer
    speech_synthesizer: SpeechSynthesizer
    commands_context: CommandsContext

    mode: Mode
    ignore_responses: list[ResponseStatus] # TODO: to Mode

    _responses: list[ResponseCache]
    _last_interaction_time: datetime

    def __init__(self, speech_recognizer: SpeechRecognizer, speech_synthesizer: SpeechSynthesizer, commands_context: CommandsContext):
        assert isinstance(speech_recognizer, SpeechRecognizer)
        assert isinstance(speech_synthesizer, SpeechSynthesizer)
        assert isinstance(commands_context, CommandsContext)

        self.speech_recognizer = speech_recognizer
        self.speech_synthesizer = speech_synthesizer
        self.commands_context = commands_context
        commands_context.delegate = self

        self.mode = Mode.active
        self.ignore_responses = []
        self._responses = []
        self._last_interaction_time = datetime.now()

    @property
    def timeout_reached(self):
        return (datetime.now() - self._last_interaction_time).total_seconds() >= self.mode.timeout_after_interaction

    # SpeechRecognizerDelegate

    async def speech_recognizer_did_receive_final_result(self, result: str):
        if os.getenv("STARK_VOICE_CLI", "0") == "1":
            print(f'\nYou: {result}')
        else:
            logger.info(f'You: {result}')
        # check explicit interaction if needed
        if pattern_str := self.mode.explicit_interaction_pattern:
            if not await Pattern(pattern_str).match(result):
                return

        # reset context if timeout reached
        if self.timeout_reached:
            self.commands_context.pop_to_root_context()

        self._last_interaction_time = datetime.now()

        # switch mode if needed
        if self.mode.mode_on_interaction:
            self.mode = self.mode.mode_on_interaction()

        await self.commands_context.process_string(result)

    async def speech_recognizer_did_receive_partial_result(self, result: str):
        if os.getenv("STARK_VOICE_CLI", "0") == "1":
            print(f'\rYou: \x1B[3m{result}\x1B[0m', end = '')

    async def speech_recognizer_did_receive_empty_result(self):
        pass

    # CommandsContextDelegate

    async def commands_context_did_receive_response(self, response: Response):

        if response.status in self.ignore_responses:
            return

        timeout_before_repeat = self.mode.timeout_before_repeat

        if self.timeout_reached and self.mode.mode_on_timeout:
            self.mode = self.mode.mode_on_timeout()

        if self.timeout_reached and self.mode.collect_responses:
            self._responses.append(ResponseCache(**response.dict(), timeout_before_repeat = timeout_before_repeat))

        # play response if needed

        if not self.mode.play_responses:
            return

        await self._play_response(response)

        if self.timeout_reached:
            return

        # repeat responses if interaction was recently

        while self._responses:
            response = self._responses.pop(0)
            if (datetime.now() - response.time).total_seconds() <= response.timeout_before_repeat:
                self._responses.insert(0, response)
                continue

            await self._play_response(response)
            self.commands_context.add_context(CommandsContextLayer(response.commands, response.parameters))

            if response.needs_user_input:
                break
        else:
            if self.mode.stop_after_interaction:
                self.speech_recognizer.stop_listening()

    def remove_response(self, response: Response):
        if response in self._responses:
            self._responses.remove(cast(ResponseCache, response))

    # Private

    async def _play_response(self, response: Response):
        self.commands_context.last_response = response

        if response.text:
            if os.getenv("STARK_VOICE_CLI", "0") == "1":
                print(f'S.T.A.R.K.: {response.text}')
            else:
                logger.info(f'S.T.A.R.K.: {response.text}')

        if response.voice:
            was_recognizing = self.speech_recognizer.is_recognizing
            self.speech_recognizer.is_recognizing = False
            speech = await self.speech_synthesizer.synthesize(response.voice)
            await speech.play()
            self.speech_recognizer.is_recognizing = was_recognizing
