from google.cloud import texttospeech
import os
import pygame
import time
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "Text2Speech/archie-test-key.json"

class speech:
    def __init__(this, text, voice, path):
        this._text  = text
        this._voice = voice
        this._path  = path

    def speak(this):
        print(f'Говорю: {this._text}')
        pygame.mixer.init()
        pygame.mixer.music.load(this._path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy() == True:
            time.sleep(0.1)

class engine:
    def __init__(this, name = 'ru-RU-Wavenet-B'):
        # os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "archie-test-key.json"
        this._name         = name
        this._client       = texttospeech.TextToSpeechClient()
        this._audio_config = texttospeech.AudioConfig( audio_encoding = texttospeech.AudioEncoding.MP3 )
        this._voice        = texttospeech.VoiceSelectionParams(
            language_code  = 'ru-RU',
            name           = name,
            ssml_gender    = texttospeech.SsmlVoiceGender.FEMALE)

    def generate(this, text):
        synthesis_input = texttospeech.SynthesisInput(text=text)
        response        = this._client.synthesize_speech(input = synthesis_input, voice = this._voice, audio_config = this._audio_config)
        dir             = f'audio/{this._name}/'
        path            = f'{dir}/{text}.mp3'
        if not os.path.exists(dir): os.makedirs(dir)
        if not os.path.exists(path):
            with open(path, 'wb') as out:
                out.write(response.audio_content)
        return speech(text, this._name, path)
