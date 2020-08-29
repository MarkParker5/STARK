from google.cloud import texttospeech
import os
from pygame import mixer
from  time import sleep
import mmap
import config

class Speech:
    _list = []
    def __init__(this, text, voice, path, standart = False):
        this._text      = text
        this._voice     = voice
        this._path      = path
        this._standart  = standart
        if(standart): Speech.append(this)

    def speak(this):
        if( os.path.exists(this._path) ):
            with open(this._path) as f:
                with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as audio:
                    mixer.init()
                    mixer.music.load(audio)
                    mixer.music.play()
                    while mixer.music.get_busy():
                        sleep(0.1)
            if(not this._standart): os.remove(this._path)

    def getBytes(this):
        return open(this._path, 'rb')

    def getPath(this):
        return this._path

    @staticmethod
    def append(obj):
        Speech._list.append(obj)

    @staticmethod
    def getList():
        return Speech._list

class Engine:
    def __init__(this, name = 'ru-RU-Wavenet-B', language_code = config.language_code):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = config.goole_tts_json_key
        this._client       = texttospeech.TextToSpeechClient()
        this._audio_config = texttospeech.AudioConfig( audio_encoding = texttospeech.AudioEncoding.MP3 )
        this._language_code= language_code
        this._name         = name
        this._voice        = texttospeech.VoiceSelectionParams(
            language_code  = this._language_code,
            name           = this._name,
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

    def generate(this, text, standart = False):
        dir             = f'audio/{this._name}'
        path            = f'{dir}/{Engine.transliterate(text)[:100]}.mp3'
        if( os.path.exists(path) ): return Speech(text, this._name, path, standart)
        synthesis_input = texttospeech.SynthesisInput(text=text)
        response        = this._client.synthesize_speech(input = synthesis_input, voice = this._voice, audio_config = this._audio_config)
        if not os.path.exists(dir): os.makedirs(dir)
        with open(path, 'wb') as out:
            out.write(response.audio_content)
        return Speech(text, this._name, path, standart)
