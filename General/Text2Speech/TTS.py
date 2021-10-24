from google.cloud import texttospeech
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
from pygame import mixer
from  time import sleep
import mmap
import config

class Speech:
    _list = []
    def __init__(self, text, voice, path, standart = False):
        self._text      = text
        self._voice     = voice
        self._path      = path
        self._standart  = standart
        if(standart): Speech.append(self)

    def speak(self):
        if not os.path.exists(self._path): return
        with open(self._path) as f:
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as audio:
                mixer.init()
                mixer.music.load(audio)
                mixer.music.set_volume(config.voice_volume)
                mixer.music.play()
                while mixer.music.get_busy():
                    sleep(0.1)
        if(not self._standart): os.remove(self._path)

    def getBytes(self):
        if not os.path.exists(self._path): return None
        with open(self._path, 'rb') as b:
            bytes = b
        return bytes

    def getPath(self):
        return self._path

    @staticmethod
    def append(obj):
        Speech._list.append(obj)

    @staticmethod
    def getList():
        return Speech._list

class Engine:
    def __init__(self, name = 'ru-RU-Wavenet-B', language_code = config.language_code):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = config.goole_tts_json_key
        self._client       = texttospeech.TextToSpeechClient()
        self._audio_config = texttospeech.AudioConfig( audio_encoding = texttospeech.AudioEncoding.MP3 )
        self._language_code= language_code
        self._name         = name
        self._voice        = texttospeech.VoiceSelectionParams(
            language_code  = self._language_code,
            name           = self._name,
            ssml_gender    = texttospeech.SsmlVoiceGender.FEMALE)

    @staticmethod
    def transliterate(name):
        dict = {'а':'a','б':'b','в':'v','г':'g','д':'d','е':'e','ё':'e',
          'ж':'zh','з':'z','и':'i','й':'i','к':'k','л':'l','м':'m','н':'n',
          'о':'o','п':'p','р':'r','с':'s','т':'t','у':'u','ф':'f','х':'h',
          'ц':'c','ч':'cz','ш':'sh','щ':'scz','ы':'y','э':'e',
          'ю':'u','я':'ja'}
        allowed = 'abcdefghijklmnopqrstuvxyz'
        name = name.lower()
        for i, letter in enumerate(name):
            if letter in allowed: continue;
            if letter in dict.keys(): name = name.replace(letter, dict[letter])
            else: name = name.replace(letter, '_')
        return name

    def generate(self, text, standart = False):
        dir             = f'audio/{self._name}'
        path            = f'{dir}/{Engine.transliterate(text)[:100]}.mp3'
        if( os.path.exists(path) ): return Speech(text, self._name, path, standart)
        synthesis_input = texttospeech.SynthesisInput(text=text)
        try:
            response        = self._client.synthesize_speech(input = synthesis_input, voice = self._voice, audio_config = self._audio_config)
            if not os.path.exists(dir): os.makedirs(dir)
            with open(path, 'wb') as out:
                out.write(response.audio_content)
        except:
            print("[ERROR] TTS Error: google cloud tts response error. Check Cloud Platform Console")
        return Speech(text, self._name, path, standart)
