from typing import Generator
import anyio
from stark.interfaces.protocols import SpeechRecognizer
from stark.models.transcription import KaldiMBR, KaldiWord


class RecognizerRelay:
    
    current_requests: dict[str, KaldiMBR]
    
    def __init__(self):
        self.current_requests = {}
    
    def _build_best_confidence(self, tracks: set[KaldiMBR], until: float | None = None) -> KaldiMBR:
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
            other = self._build_best_confidence(tracks - {longest}, until = end)
            
            # Compare two tracks
            
            base_word = longest.result.pop(0)
            alternative_words = list(self._pop_words_until_time(other, end))
            
            if not alternative_words:
                best.result.append(base_word)
                continue
            
            # build complex
            complex_alternative = KaldiWord(word = '', start = base_word.start, end = base_word.end)
            complex_alternative.word = ' '.join(word.word for word in alternative_words)
            complex_alternative.end = max(word.end for word in alternative_words)
            complex_alternative.start = min(word.start for word in alternative_words)
            complex_alternative.conf = sum(word.conf or 0 for word in alternative_words) / len(alternative_words) # TODO: conf * dutation instead of AVG
            complex_alternative.language_code = alternative_words[0].language_code # TODO: improve
            
            if complex_alternative.conf == base_word.conf and base_word.language_code == 'ru-RU': # attempt of native language priority TODO: fix
                best.result.append(base_word)
            elif(base_word.conf or 0) > (complex_alternative.conf or 0): # TODO: conf * dutation instead of AVG
                best.result.append(base_word)
            else:
                best.result.append(complex_alternative)
            
        best.text = ' '.join(word.word for word in best.result)
            
        return best
    
    def _pop_words_until_time(self, track: KaldiMBR, time: float) -> Generator[KaldiWord, None, None]:
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
            print(lang, '\t', request.confidence, '\t', ''.join([f'[{w.word}]' for w in request.result]))
        
        self.current_requests['best'] = self._build_best_confidence(set(self.current_requests.values()))
        self.current_requests['best'].language_code = 'best'
        
        print(self.current_requests['best'].language_code, '\t', self.current_requests['best'].confidence, '\t', ''.join([f'[{w.word}]' for w in self.current_requests['best'].result]))
            
        self.current_requests = {}
        # process; TODO: VA
    
    async def speech_recognizer_did_receive_partial_result(self, result: str): 
        pass
    
    async def speech_recognizer_did_receive_empty_result(self): 
        pass
