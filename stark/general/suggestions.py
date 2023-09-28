import numpy as np
from dataclasses import dataclass
import subprocess
import re
import warnings
from stark.models.transcription import Transcription


@dataclass
class KeywordMeta:
    keyword: str
    variant: str
    simple_phonetic: str
    caverphone: str
    language_code: str | None = None

class SuggestionsManager:
    
    keywords: dict[str, dict[str, KeywordMeta]] # keyword: {origin: KeywordMeta}
    
    def __init__(self):
        self.keywords = {}
        
    def add_keyword(self, keyword: str, variant: str | None = None, language_code: str = 'en', multilingual: bool = False):
        variant = variant or keyword
        
        if not self.keywords.get(keyword):
            self.keywords[keyword] = {}
        elif variant in self.keywords[keyword]:
            return
        
        simple_phonetic = self._ipa_to_latin(self._espeak(variant, language_code))
        caverphone = self._caverphone1(simple_phonetic)
        
        self.keywords[keyword][variant] = KeywordMeta(keyword, variant, simple_phonetic, caverphone, language_code if multilingual else None)
        
        if keyword != variant:
            self.add_keyword(keyword, None, language_code, multilingual)
            
    def add_transcription_suggestions(self, transcription: Transcription):
        # TODO: caching
        for language, track in transcription.origins.items():
            transcription.suggestions.extend(self.get_string_suggestions(track.text, language))
            
    def get_string_suggestions(self, string: str, language_code: str) -> set[tuple[str, str]]:
        suggestions: set[tuple[str, str]] = set()
        
        for variants in self.keywords.values():
            for variant in variants.values():
                
                match_language = variant.language_code is None or variant.language_code == language_code
                
                if match_language and (substring := self._search(variant, string, language_code)):
                    suggestions.add((substring, variant.keyword))
                        
        return suggestions
    
    # private
    
    def _search(self, keyword: KeywordMeta, string: str, language_code: str) -> str | None:
        if self._customphone(string) == keyword.caverphone:
            return string
        
        phonetic = self._ipa_to_latin(self._espeak(string, language_code))
        
        caverphone_substring = lambda: self._levenshtein(keyword.caverphone, self._customphone(phonetic) or '', 0)
        phonetic_substring = lambda: self._levenshtein(keyword.simple_phonetic, phonetic, 0.1)
            
        # return caverphone_substring() or phonetic_substring()
        return '' # TODO: back transformation to get original substring

    def _espeak(self, string: str, language_code: str) -> str:
        result = subprocess.run(['espeak', '--ipa', f'-v{language_code}', '-q', string], capture_output=True, text=True)
        return re.compile(r'\(.*?\)').sub('', result.stdout.strip()).strip()
        
    def _customphone(self, word: str) -> str | None:
        '''Caverphone 2.0 based algorithm for phonetic encoding of words. No filling with "1", no length limit, return None if word is empty.'''
        
        alphabet = "abcdefghijklmnopqrstuvwxyz"
        vowels = "aeiou"

        word = word.lower()
        word = "".join(_w for _w in word if _w in alphabet)
        
        if not word:
            return None

        if word[-1:] == "e":
            word = word[0:-1]

        if word[0:5] == "cough":
            word = "cou2f" + word[5:]
        if word[0:5] == "rough":
            word = "rou2f" + word[5:]
        if word[0:5] == "tough":
            word = "tou2f" + word[5:]
        if word[0:6] == "enough":
            word = "enou2f" + word[5:]
        if word[0:6] == "trough":
            word = "trou2f" + word[5:]
        if word[0:2] == "gn":
            word = "2n" + word[2:]
        if word[-2:] == "mb":
            word = word[0:-2] + "m2"

        word = word.replace("cq", "2q")
        word = word.replace("ci", "si")
        word = word.replace("ce", "se")
        word = word.replace("cy", "sy")
        word = word.replace("tch", "2ch")
        word = word.replace("c", "k")
        word = word.replace("q", "k")
        word = word.replace("x", "k")
        word = word.replace("v", "f")
        word = word.replace("dg", "2g")
        word = word.replace("tio", "sio")
        word = word.replace("tia", "sia")
        word = word.replace("d", "t")
        word = word.replace("ph", "fh")
        word = word.replace("b", "p")
        word = word.replace("sh", "s2")
        word = word.replace("z", "s")

        if word[0:1] in vowels:
            word = "A" + word[1:]
        for _v in vowels:
            word = word.replace(_v, "3")

        word = word.replace("j", "y")
        word = word.replace("y3", "Y3")

        if word[0:2] == "y3":
            word = "Y3" + word[2:]
        if word[0] == "y":
            word = "A" + word[1:]

        word = word.replace("y", "3")
        word = word.replace("3gh3", "3kh3")
        word = word.replace("gh", "22")
        word = word.replace("g", "k")

        for _w in "stpkfmn":
            while _w * 2 in word:
                word = word.replace(_w * 2, _w)
            word = word.replace(_w, _w.upper())

        word = word.replace("w3", "W3")
        word = word.replace("wh3", "Wh3")

        if word[-1:] == "w":
            word = word[0:-1] + "3"

        word = word.replace("w", "2")

        if word[0:1] == "h":
            word = "A" + word[1:]

        word = word.replace("h", "2")
        word = word.replace("r3", "R3")

        if word[-1:] == "r":
            word = word[0:-1] + "3"

        word = word.replace("r", "2")
        word = word.replace("l3", "L3")

        if word[-1:] == "l":
            word = word[0:-1] + "3"

        word = word.replace("l", "2")
        word = word.replace("2", "")

        if word[-1:] == "3":
            word = word[0:-1] + "A"

        word = word.replace("3", "")
        
        # while len(word) < 10:
        #     word += '1'
        
        if word == 'A':
            return None

        return word
        
    def _levenshtein(self, query: str, string: str, trashhold: float) -> str | None:
        if not query or not string:
            return None
        
        max_distance = int(max(len(query), len(string)) * trashhold)
        n = len(query)
        m = len(string)
        best_distance = float('inf')
        suggested_substring = None
        
        for i in range(m - n + 1):
            substring = string[i:i + n]
            dp = np.zeros((n + 1, 2), dtype=int)
            dp[:, 0] = np.arange(n + 1)
            
            for j in range(1, n + 1):
                dp[j, 1] = min(
                    dp[j - 1, 0] + 1,
                    dp[j, 0] + 1,
                    dp[j - 1, 1] + (query[j - 1] != substring[j - 1])
                )
            
            distance = dp[-1, 1]
            if distance < best_distance:
                best_distance = distance
                suggested_substring = substring
                
            if best_distance <= max_distance:
                break
        
        if best_distance <= max_distance:
            return suggested_substring
        else:
            return None
        
    def _ipa_to_latin(self, origin: str) -> str:
        mapping = {
            # Vowels
            'i': 'i', 'y': 'i', 'ɨ': 'i', 'ʉ': 'u', 'ɯ': 'u', 'u': 'u',
            'ɪ': 'i', 'ʏ': 'i', 'ʊ': 'u',
            'e': 'e', 'ø': 'e', 'ɘ': 'e', 'ɵ': 'o', 'ɤ': 'o', 'o': 'o',
            'ə': 'e',
            'ɛ': 'e', 'œ': 'e', 'ɜ': 'e', 'ɞ': 'e', 'ʌ': 'a', 'ɔ': 'o',
            'æ': 'a', 'ɐ': 'a', 'a': 'a', 'ɶ': 'a', 'ä': 'a', 'ɑ': 'a', 'ɒ': 'o',

            # Pulmonic Consonants
            'p': 'p', 'b': 'b', 't': 't', 'd': 'd', 'ʈ': 't', 'ɖ': 'd', 'c': 'k', 'ɟ': 'j', 'k': 'k', 'g': 'g', 'q': 'k', 'ɢ': 'g', 'ɡ': 'g',
            'm': 'm', 'ɱ': 'm', 'n': 'n', 'ɳ': 'n', 'ɲ': 'nj', 'ŋ': 'ng',
            'ʋ': 'v', 'ɹ': 'r', 'ɻ': 'r', 'j': 'j', 'ɰ': 'w',
            'ʙ': 'b', 'r': 'r', 'ʀ': 'r',
            'ɸ': 'f', 'β': 'v', 'f': 'f', 'v': 'v', 'θ': 'th', 'ð': 'dh', 's': 's', 'z': 'z', 'ʃ': 'sh', 'ʒ': 'zh', 'ʂ': 'sh', 'ʐ': 'zh', 'ç': 'h', 
            'ʝ': 'j', 'x': 'h', 'ʑ': 'z', 'ɣ': 'gh', 'χ': 'h', 'ʁ': 'gh', 'ħ': 'h', 'ʕ': 'a', 'h': 'h',

            # Clicks
            'ʘ': 'o', 'ǀ': 'l', 'ǃ': '!', 'ǂ': '!', 'ǁ': 'l',

            # Implosives and Ejectives
            'ɓ': 'b', 'ɗ': 'd', 'ʄ': 'j', 'ɠ': 'g', 'ʛ': 'g',

            # Suprasegmentals
            'ˈ': '', 'ˌ': '', 'ː': '', 'ˑ': '', '|': '', '‖': '', '.': '', 'ʼ': '',

            # Tones and word accents
            '̋': '', '́': '', '̄': '', '̀': '', '̏': '', '̌': '', '̂': '', '᷄': '', '᷅': '', '᷈': '', '᷉': '', 

            # Other symbols and diacritics
            'ʲ': '', 'ʷ': 'w', 'ʱ': 'h', 'ʰ': 'h', 'ʴ': 'r', 'ʳ': 'r', 'ˠ': 'g', 'ʼ': '', 'ʡ': 'a', 'ʢ': 'a', 'ɭ': 'l', ' ': '', '_': '', '"': '', ' ': ''
        }

        string = origin
        for ipa, simple in mapping.items():
            string = string.replace(ipa, simple)
            
        for symbol in string:
            if not symbol in 'qwertyuiopasdfghjklzxcvbnm':
                warnings.warn(f'SuggestionsManager._ipa_to_latin: Unknown symbol: "{symbol}" in {string} ({origin})')
        
        return string
