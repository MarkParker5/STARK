import asyncio

from VICore import CommandsContext, CommandsContextDelegate
from IO.SpeechRecognition import SpeechRecognizer, SpeechRecognizerDelegate
from IO import Text2Speech


class VoiceAssistant(SpeechRecognizerDelegate, CommandsContextDelegate):

    speech_recognizer: SpeechRecognizer
    commands_context: CommandsContext
    voice = Text2Speech.Engine()

    voids: int = 0
    last_clap_time: float = 0
    double_clap: bool = False

    # Control

    def __init__(self, commands_context: CommandsContext):
        self.speech_recognizer = SpeechRecognizer(delegate = self)
        self.commands_context = commands_context
        commands_context.delegate = self

    def start(self):
        self.speech_recognizer.delegate = self
        print('Listen...')
        asyncio.get_event_loop().run_until_complete(
            self.speech_recognizer.startListening()
        )

    def stop(self):
        self.speech_recognizer.stopListening()

    # SpeechRecognizerDelegate

    def speech_recognizer_did_receive_final_result(self, result: str):
        self.voids = 0
        # self.commands_context.lastInteractTime = VITime()
        print(f'\rYou: {result}')

        self.commands_context.process_string(result)

    def speech_recognizer_did_receive_partial_result(self, result: str):
        print(f'\rYou: \x1B[3m{result}\x1B[0m', end = '')

    def speech_recognizer_did_receive_empty_result(self):
        self.voids += 1

    # CommandsContextDelegate

    def commands_context_did_receive_response(self, response):
        if response.text:
            print(f'Archie: {response.text}')
        if response.voice:
            was_recognizing = self.speech_recognizer.is_recognizing
            self.speech_recognizer.is_recognizing = False
            self.voice.generate(response.voice).speak()
            self.speech_recognizer.is_recognizing = was_recognizing