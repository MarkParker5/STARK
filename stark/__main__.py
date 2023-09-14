from VICore import CommandsContext
from VoiceAssistant import VoiceAssistant
from IO.VoskSpeechRecognizer import VoskSpeechRecognizer
from IO.GCloudSpeechSynthesizer import GCloudSpeechSynthesizer
from IO.SileroSpeechSynthesizer import SileroSpeechSynthesizer
from features import default


if __name__ == '__main__':
    cm = CommandsContext(commands_manager = default)
    va = VoiceAssistant(
        speech_recognizer = VoskSpeechRecognizer(),
        speech_synthesizer = SileroSpeechSynthesizer(), # or GCloudSpeechSynthesizer()
        commands_context = cm
    )
    
    va.start()
