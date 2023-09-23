# import anyio
# from stark import run, CommandsManager, Response
# from stark.interfaces.vosk import VoskSpeechRecognizer
# from stark.interfaces.silero import SileroSpeechSynthesizer


# vosk_model_ur = 'https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip'
# vosk_speaker_model_ur: str | None = 'https://alphacephei.com/vosk/models/vosk-model-spk-0.4.zip'
# silero_model_ur = 'https://models.silero.ai/models/tts/ru/ru_v3.pt'

# recognizer = VoskSpeechRecognizer(model_url = vosk_model_ur, speaker_model_url = vosk_speaker_model_ur)
# synthesizer = SileroSpeechSynthesizer(model_url = silero_model_ur)

# manager = CommandsManager()

# @manager.new('привет')
# async def hello_command() -> Response:
#     text = voice = 'Привет!'
#     return Response(text=text, voice=voice)

# async def main():
#     await run(manager, recognizer, synthesizer)

# if __name__ == '__main__':
#     anyio.run(main)



from typing import Generator
import anyio
import asyncer
from stark import run, CommandsManager, Response
from stark.interfaces.protocols import SpeechRecognizer
from stark.interfaces.vosk import VoskSpeechRecognizer, KaldiMBR, KaldiTranscriptionWord, MicrophoneListener
from stark.interfaces.silero import SileroSpeechSynthesizer


vosk_model_url_ru = 'https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip'
vosk_model_url_en = 'https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip'
# vosk_speaker_model_url: str | None = 'https://alphacephei.com/vosk/models/vosk-model-spk-0.4.zip'
# silero_model_url = 'https://models.silero.ai/models/tts/ru/ru_v3.pt'

class RecognizerRelay:
    
    current_requests: dict[str, KaldiMBR]
    
    def __init__(self):
        self.current_requests = {}
    
    def build_best_confidence(self, tracks: set[KaldiMBR], until: float | None = None) -> KaldiMBR:
        if not tracks: return KaldiMBR()
        
        best = KaldiMBR()
        
        while tracks:
            # check tracks are not empty within `until`
            
            tracks = set(filter(lambda track: track.result and (until is None or track.result[0].middle < until), tracks))
            
            if not tracks:
                break
            
            # reqursive part: go down to min by removing max and limiting to end=min(max.end, until) where until is previous level end
            
            longest = max(tracks, key = lambda track: track.result[0].end if until is None or track.result[0].middle < until else 0)
            end = min(longest.result[0].end, until) if not until is None else longest.result[0].end
            other = self.build_best_confidence(tracks - {longest}, until = end)
            
            # Compare two tracks
            
            base_word = longest.result.pop(0)
            alternative_words = list(self.pop_words_until_time(other, end))
            complex_alternative = KaldiTranscriptionWord(word = '', start = base_word.start, end = base_word.end)
            
            # build complex
            complex_alternative.word = ' '.join(word.word for word in alternative_words)
            complex_alternative.end = max(word.end for word in alternative_words)
            complex_alternative.start = min(word.start for word in alternative_words)
            complex_alternative.conf = sum(word.conf or 0 for word in alternative_words) / len(alternative_words) # TODO: conf * dutation instead of AVG
            complex_alternative.language_code = alternative_words[0].language_code # TODO: improve
            
            # if the longest is the only one (`alternative_words` is empty), complex will be empty (conf=0)
            
            if complex_alternative.conf == base_word.conf and base_word.language_code == 'ru-RU': # attempt of native language priority
                best.result.append(base_word)
            elif(base_word.conf or 0) > (complex_alternative.conf or 0): # TODO: conf * dutation instead of AVG
                best.result.append(base_word)
            else:
                best.result.append(complex_alternative)
            
        best.text = ' '.join(word.word for word in best.result)
            
        return best
    
    def pop_words_until_time(self, track: KaldiMBR, time: float) -> Generator[KaldiTranscriptionWord, None, None]:
        for word in track.result:
            if word.middle > time:
                break
            track.result.remove(word)
            yield word
        
    # SpeechRecognizerDelegate Protocol Implmenetation
    
    async def speech_recognizer_did_receive_final_result(self, speech_recognizer: SpeechRecognizer, result: KaldiMBR): 
        # NOTE: this executes for each SR, be aware of duplicating output
        
        self.current_requests[result.language_code] = result
        
        await anyio.sleep(2) # wait other languages
        
        if not self.current_requests: # TODO: avoid duplicating because of multiple SRs
            return
        
        # build best confedence
        
        print('\n--------------------------\n')
        for lang, request in self.current_requests.items():
            print(lang, '\t', request.confidence, '\t', request.text)
        
        self.current_requests['best'] = self.build_best_confidence(set(self.current_requests.values()))
        
        print(self.current_requests['best'].language_code, '\t', self.current_requests['best'].confidence, '\t', self.current_requests['best'].text)
            
        self.current_requests = {}
        # process; TODO: VA
    
    async def speech_recognizer_did_receive_partial_result(self, result: str): 
        pass
    
    async def speech_recognizer_did_receive_empty_result(self): 
        pass
    

async def main():
    async with asyncer.create_task_group() as main_group:
        
        recognizer1 = VoskSpeechRecognizer('ru-RU', model_url = vosk_model_url_ru)
        recognizer2 = VoskSpeechRecognizer('en-US', model_url = vosk_model_url_en)
        recognizers = [recognizer1, recognizer2]
        relay = RecognizerRelay()
        
        def microphone_callback(data):
            for recognizer in recognizers:
                recognizer.microphone_did_receive_sample(data)
                
        microphone = MicrophoneListener(microphone_callback)
        
        main_group.soonify(microphone.start_listening)()
        for recognizer in recognizers:    
            recognizer.delegate = relay
            main_group.soonify(recognizer.start_listening)()
            
        # while True:
        #     await anyio.sleep(0.01)
            
    # await run(manager, recognizer, synthesizer)

if __name__ == '__main__':
    anyio.run(main)
