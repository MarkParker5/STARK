import os
import numpy
import torch
import sounddevice
from .protocols import SpeechSynthesizer, SpeechSynthesizerResult


class Speech(SpeechSynthesizerResult):

    def __init__(self, audio: numpy.ndarray, sample_rate: int):
        self.audio = audio
        self.sample_rate = sample_rate

    def play(self):
        sounddevice.play(self.audio, self.sample_rate, blocking = True)

    def stop(self):
        pass

class SileroSpeechSynthesizer(SpeechSynthesizer):
    
    def __init__(self, model_url: str, speaker = 'baya', threads = 4, device ='cpu'):
        torch.backends.quantized.engine = 'qnnpack'
        device = torch.device(device)
        torch.set_num_threads(threads)
        local_file = 'downloads/' + model_url.split('/')[-1]
        
        if not os.path.isdir('downloads'):
            os.mkdir('downloads')

        if not os.path.isfile(local_file):
            torch.hub.download_url_to_file(model_url, local_file)
            
        self.model = torch.package.PackageImporter(local_file).load_pickle('tts_models', 'model')
        self.model.to(device)
        self.sample_rate = 24000
        self.speaker = speaker

    def synthesize(self, text) -> Speech:
        audio = self.model.apply_tts(text = text, speaker = self.speaker, sample_rate = self.sample_rate)
        return Speech(audio, self.sample_rate)