import asyncio
from datetime import datetime

from VICore import CommandsContext, CommandsContextLayer, CommandsContextDelegate, Response
from IO.protocols import SpeechRecognizer, SpeechRecognizerDelegate, SpeechSynthesizer, SpeechSynthesizerResult


class VoiceAssistant(SpeechRecognizerDelegate, CommandsContextDelegate):

    speech_recognizer: SpeechRecognizer
    speech_synthesizer: SpeechSynthesizer
    commands_context: CommandsContext
    
    _responses: list[Response] = []
    _last_interaction_time: datetime

    def __init__(self, speech_recognizer: SpeechRecognizer, speech_synthesizer: SpeechSynthesizer, commands_context: CommandsContext):
        self.speech_recognizer = speech_recognizer
        self.speech_synthesizer = speech_synthesizer
        self.commands_context = commands_context
        commands_context.delegate = self
        
        self._last_interaction_time = datetime.now()

    @property
    def inactive(self):
        return (datetime.now() - self._last_interaction_time).total_seconds() > 30

    # Control

    def start(self):
        self.speech_recognizer.delegate = self
        print('Listen...')
        asyncio.get_event_loop().run_until_complete(
            self.speech_recognizer.start_listening()
        )

    def stop(self):
        self.speech_recognizer.stop_listening()

    # SpeechRecognizerDelegate

    def speech_recognizer_did_receive_final_result(self, result: str):
        
        if self.inactive:
            self.commands_context.pop_to_root_context()
        
        print(f'\rYou: {result}')
        self._last_interaction_time = datetime.now()
        self.commands_context.process_string(result)
        
        # repeat responses
        while response := self._responses.pop(0):
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
        if self.inactive:
            self._responses.append(response)
            
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