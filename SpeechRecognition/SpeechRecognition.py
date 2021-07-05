import speech_recognition as sr
import config

#r = sr.Recognizer()
#m = sr.Microphone(device_index=config.device_index)

class SpeechToText:
    def __init__(this, device = config.device_index, language = config.language_code):
        this.device     = device
        this.language   = language
        this.m          = sr.Microphone(device_index = this.device)
        this.r          = sr.Recognizer()
        this.r.pause_threshold          = config.pause_threshold
        this.r.energy_threshold         = config.energy_threshold
        this.r.dynamic_energy_threshold = config.dynamic_energy_threshold
        this.r.non_speaking_duration    = config.non_speaking_duration

    def listen(this):
        try:
            with this.m as source:
                audio = this.r.listen(source)
        except:
            return ''
        try:
            responce = {'text': this.r.recognize_google(audio, language = this.language).lower(), 'status': 'ok'}
        except sr.UnknownValueError:
            responce = {'text': None, 'status': 'void'}
        except sr.RequestError:
            responce = {'text': None, 'status': 'error'}
        return responce

    def recognize(this, speech):
        with sr.AudioFile(speech.getPath()) as source:
            audio = r.record(source)
        try:
            return r.recognize_google(audio)
        except:
            return ''

    def listen_noise(this):
        with this.m as source:
            this.r.adjust_for_ambient_noise(source)

    def set_device(this, index):
        this.device = 1
        this.m = sr.Microphone(device_index = this.device)
