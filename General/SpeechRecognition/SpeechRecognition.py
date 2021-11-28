import speech_recognition as sr
import config

#r = sr.Recognizer()
#m = sr.Microphone(device_index=config.device_index)

class SpeechToText:
    def __init__(self, device = config.device_index, language = config.language_code):
        self.device     = device
        self.language   = language
        self.m          = sr.Microphone(device_index = self.device)
        self.r          = sr.Recognizer()
        self.r.pause_threshold          = config.pause_threshold
        self.r.energy_threshold         = config.energy_threshold
        self.r.dynamic_energy_threshold = config.dynamic_energy_threshold
        self.r.non_speaking_duration    = config.non_speaking_duration

    def listen(self):
        try:
            with self.m as source:
                audio = self.r.listen(source)
        except:
            return ''
        try:
            responce = {'text': self.r.recognize_google(audio, language = self.language).lower(), 'status': 'ok'}
        except sr.UnknownValueError:
            responce = {'text': None, 'status': 'void'}
        except sr.RequestError:
            responce = {'text': None, 'status': 'error'}
        return responce

    def recognize(self, speech):
        with sr.AudioFile(speech.getPath()) as source:
            audio = r.record(source)
        try:
            return r.recognize_google(audio)
        except:
            return ''

    def listen_noise(self):
        with self.m as source:
            self.r.adjust_for_ambient_noise(source)

    def set_device(self, index):
        self.device = 1
        self.m = sr.Microphone(device_index = self.device)