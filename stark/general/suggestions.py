from dataclasses import dataclass
from stark.models.transcription import Transcription
from .strings.levenshtein import levenshtein
from .strings.starkophone import starkophone as get_starkophone
from .strings.ipa import ipa_to_latin, string_to_ipa
from .strings.find_substring_in_words import find_substring_in_words


@dataclass
class KeywordMeta:
    keyword: str
    variant: str
    phonetic: str
    starkophone: str
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
        
        simple_phonetic = self._get_phonetic(variant, language_code)
        starkophone = ' '.join([word for word in [get_starkophone(word) for word in simple_phonetic.split()] if word])
        
        self.keywords[keyword][variant] = KeywordMeta(keyword, variant, simple_phonetic, starkophone, language_code if not multilingual else None)
        
        if keyword != variant:
            self.add_keyword(keyword, None, language_code, multilingual)
            
    def add_transcription_suggestions(self, transcription: Transcription):
        for language, track in transcription.origins.items():
            transcription.suggestions.extend(self.get_string_suggestions(track.text, language))
            
    def get_string_suggestions(self, string: str, language_code: str) -> set[tuple[str, str]]:
        # TODO: cache all long shit
        
        suggestions: set[tuple[str, str]] = set()
        
        phonetic_string = self._get_phonetic(string, language_code)
        starkophone_string = get_starkophone(phonetic_string) or ''
        words = string.split()
        phonetic_words = phonetic_string.split()
        starkophone_words = starkophone_string.split()
        
        for variants in self.keywords.values():
            for variant in variants.values():
                if variant.language_code and variant.language_code != language_code:
                    continue
                
                matches: list[list[int]] = []
                for phonetic_substrings in levenshtein(variant.phonetic, phonetic_string, 0.2):
                    matches.extend(find_substring_in_words(phonetic_substrings, phonetic_words))
                    
                for starkophone_substrings in levenshtein(variant.starkophone, starkophone_string, 0.1):
                    matches.extend(find_substring_in_words(starkophone_substrings, starkophone_words))
                    
                for match in matches:
                    substring = ' '.join(words[i] for i in match)
                    suggestions.add((substring, variant.keyword))
                
        return suggestions
    
    # private
    
    def _get_phonetic(self, string: str, language_code: str) -> str:
        return ' '.join(ipa_to_latin(string_to_ipa(word, language_code)) for word in string.split())
