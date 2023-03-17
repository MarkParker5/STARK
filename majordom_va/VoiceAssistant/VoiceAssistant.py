import asyncio
from datetime import datetime

from VICore import (
    CommandsContext,
    CommandsContextLayer,
    CommandsContextDelegate,
    Response,
    ResponseStatus,
    Pattern
)
from IO.protocols import SpeechRecognizer, SpeechRecognizerDelegate, SpeechSynthesizer
from .Mode import Mode


class VoiceAssistant(SpeechRecognizerDelegate, CommandsContextDelegate):

    speech_recognizer: SpeechRecognizer
    speech_synthesizer: SpeechSynthesizer
    commands_context: CommandsContext
    
    mode: Mode
    ignore_responses: list[ResponseStatus]
    explicit_interaction_pattern: Pattern | None = None
    
    _responses: list[Response]
    _last_interaction_time: datetime

    def __init__(self, speech_recognizer: SpeechRecognizer, speech_synthesizer: SpeechSynthesizer, commands_context: CommandsContext):
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

    # Control

    def start(self):
        self.speech_recognizer.delegate = self
        print('Listen...')
        asyncio.new_event_loop().run_until_complete(
            self.speech_recognizer.start_listening()
        )

    def stop(self):
        self.speech_recognizer.stop_listening()

    # SpeechRecognizerDelegate

    def speech_recognizer_did_receive_final_result(self, result: str):
        print(f'\rYou: {result}')
        
        # check explicit interaction if needed
        if self.mode.needs_explicit_interaction and self.explicit_interaction_pattern:
            if not self.explicit_interaction_pattern.match(result):
                return
        
        # reset context if timeout reached
        if self.timeout_reached:
            self.commands_context.pop_to_root_context()
        
        self._last_interaction_time = datetime.now()
        
        # save timeout_before_repeat of last mode to avoid skipping responses that were not played
        timeout_before_repeat = self.mode.timeout_before_repeat
        
        # switch mode if needed
        if self.mode.mode_on_interaction:
            self.mode = self.mode.mode_on_interaction()
        
        # main part
        self.commands_context.process_string(result)
        
        # repeat responses
        while self._responses:
            response = self._responses.pop(0)
            if (datetime.now() - response.time).total_seconds() <= timeout_before_repeat:
                continue
            
            self._play_response(response)
            self.commands_context.add_context(CommandsContextLayer(response.commands, response.parameters))
            
            if response.needs_user_input:
                break

    def speech_recognizer_did_receive_partial_result(self, result: str):
        print(f'\rYou: \x1B[3m{result}\x1B[0m', end = '')

    def speech_recognizer_did_receive_empty_result(self):
        pass

    # CommandsContextDelegate

    def commands_context_did_receive_response(self, response: Response):
        
        if response.status in self.ignore_responses:
            return
        
        if self.timeout_reached and self.mode.mode_on_timeout: 
            self.mode = self.mode.mode_on_timeout()
        
        if self.timeout_reached and self.mode.collect_responses:
            self._responses.append(response)
            
        if self.mode.play_responses:
            self._play_response(response)
        
    def remove_response(self, response: Response):
        self._responses.remove(response)
        
    # Private
    
    def _play_response(self, response: Response):
        self.commands_context.last_response = response
        if response.text:
            print(f'Archie: {response.text}')
        if response.voice:
            was_recognizing = self.speech_recognizer.is_recognizing
            self.speech_recognizer.is_recognizing = False
            self.speech_synthesizer.synthesize(response.voice).play()
            self.speech_recognizer.is_recognizing = was_recognizing