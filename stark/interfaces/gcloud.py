import os
import asyncer
import sounddevice
import soundfile
from google.cloud import texttospeech

from .protocols import SpeechSynthesizer, SpeechSynthesizerResult

import logging
logger = logging.getLogger(__name__)

class Speech(SpeechSynthesizerResult):

    def __init__(self, text, voice, path):
        self.text = text
        self.voice = voice
        self.path = path

    def play(self):
        try:
            sounddevice.play(*soundfile.read(self.path, dtype='float32'))
            sounddevice.wait()
        except Exception as e:
            logger.error('\n[Error] Can`t play audio file\n%s', e)

    def stop(self):
        pass

class GCloudSpeechSynthesizer(SpeechSynthesizer):

    def __init__(self, voice_name: str, language_code: str, json_key_path: str):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = json_key_path
        self._client       = texttospeech.TextToSpeechClient()
        self._audio_config = texttospeech.AudioConfig(audio_encoding = texttospeech.AudioEncoding.LINEAR16)
        self._language_code= language_code
        self._name         = voice_name
        self._voice        = texttospeech.VoiceSelectionParams(
            language_code  = self._language_code,
            name           = self._name,
            ssml_gender    = texttospeech.SsmlVoiceGender.FEMALE
        )

    async def synthesize(self, text) -> Speech:
        folder = f'audio/{self._name}'
        path = f'{folder}/{self._transliterate(text)[:100]}.wav'

        if os.path.exists(path):
            return Speech(text, self._name, path)

        synthesis_input = texttospeech.SynthesisInput(text = text)

        try:
            synthesize_speech_async = asyncer.asyncify(self._client.synthesize_speech)
            response = await synthesize_speech_async(input = synthesis_input, voice = self._voice, audio_config = self._audio_config)
            if not os.path.exists(folder):
                os.makedirs(folder)
            with open(path, 'wb') as out:
                out.write(response.audio_content)
        except Exception as e:
            logger.error("\n[ERROR] TTS Error: google cloud tts response error. Check Cloud Platform Console\n%s", e)

        return Speech(text, self._name, path)

    @staticmethod
    def _transliterate(name):
        dict = {'а':'a','б':'b','в':'v','г':'g','д':'d','е':'e','ё':'e',
          'ж':'zh','з':'z','и':'i','й':'i','к':'k','л':'l','м':'m','н':'n',
          'о':'o','п':'p','р':'r','с':'s','т':'t','у':'u','ф':'f','х':'h',
          'ц':'c','ч':'ch','ш':'sh','щ':'sch','ы':'y','э':'e',
          'ю':'u','я':'ja', ' ':'_'}
        allowed = 'abcdefghijklmnopqrstuvxyz'
        name = name.lower()
        for i, letter in enumerate(name):
            if letter in allowed:
                continue
            elif letter in dict.keys():
                name = name.replace(letter, dict[letter])
            else:
                name = name.replace(letter, '')
        return name
