import speech_recognition as sr
import time

r = sr.Recognizer()
m = sr.Microphone(device_index=1)

class SpeechToText:
    def __init__(this, device = 1, language = "ru-RU", pause_threshold = 0.4):
        this.device     = 1
        this.language   = language
        this.m          = sr.Microphone(device_index = this.device)
        this.r          = sr.Recognizer()
        this.r.pause_threshold          = pause_threshold
        this.r.energy_threshold         = 2000
        this.r.dynamic_energy_threshold = False

    def listen(this):
        with this.m as source:
            audio = this.r.listen(source)
        try:
            responce = {'text': this.r.recognize_google(audio, language = this.language).lower(), 'status': 'ok'}
        except sr.UnknownValueError:
            responce = {'text': None, 'status': 'void'}
        except sr.RequestError:
            responce = {'text': None, 'status': 'error'}
        return responce

    def listen_noise(this):
        with this.m as source:
            this.r.adjust_for_ambient_noise(source)

    def set_device(this, index):
        this.device = 1
        this.m = sr.Microphone(device_index = this.device)
