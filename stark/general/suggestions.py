from typing import Generator, Iterable
from dataclasses import dataclass
import subprocess
import re
import warnings
from spellwise import CaverphoneOne
from jellyfish import levenshtein_distance
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
        
        for word in string.split():
            # word = string # TODO: match few words, use "contains" instead of "equals"
            
            for variants in self.keywords.values():
                for variant in variants.values():
                    
                    suggestion = (word, variant.keyword)
                    match_language = variant.language_code is None or variant.language_code == language_code
                    unique = not suggestion in suggestions
                    
                    if match_language and unique and self._compare(variant, word, language_code):
                        suggestions.add(suggestion)
                        
        return suggestions
    
    # private
    
    def _compare(self, keyword: KeywordMeta, string: str, language_code: str) -> bool:
        if self._caverphone1(string) == keyword.caverphone:
            return True
        
        phonetic = self._ipa_to_latin(self._espeak(string, language_code))
        
        return self._caverphone1(phonetic) == keyword.caverphone \
            or self._levenshtein(phonetic, keyword.simple_phonetic) < 0.1

    def _espeak(self, string: str, language_code: str) -> str:
        result = subprocess.run(['espeak', '--ipa', f'-v{language_code}', '-q', string], capture_output=True, text=True) # TODO: read espeak docs
        return re.compile(r'\(.*?\)').sub('', result.stdout.strip()).strip()
        
    def _caverphone1(self, string: str) -> str:
        return CaverphoneOne()._pre_process(string).replace('1', '') # TODO: return None if needed
        
    def _levenshtein(self, string1: str, string2: str) -> float:
        if string1 == string2:
            return 0
        if len(string1) == 0 or len(string2) == 0:
            return 1
        return min(
            levenshtein_distance(string1, string2) for string1, string2 in [
                (string1, string2),
                # (word1.replace('W', 'V'), word2.replace('W', 'V')),
                # (word1.replace('W', 'F'), word2.replace('W', 'F')),
                # (string1.replace('W', 'V').replace('F', 'V'), string2.replace('W', 'V').replace('F', 'V')),
            ]
        ) / min(len(string1), len(string2))
        
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
