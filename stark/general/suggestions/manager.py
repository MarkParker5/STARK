from dataclasses import dataclass
from stark.models.transcription import Transcription
from .levenshtein import levenshtein
from .starkophone import starkophone as get_starkophone
from .ipa import ipa_to_latin, string_to_ipa


@dataclass
class KeywordMeta:
    keyword: str
    variant: str
    simple_phonetic: str
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
        
        simple_phonetic = ipa_to_latin(self._espeak(variant, language_code))
        starkophone = get_starkophone(simple_phonetic) or ''
        
        self.keywords[keyword][variant] = KeywordMeta(keyword, variant, simple_phonetic, starkophone, language_code if multilingual else None)
        
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
        if get_starkophone(string) == keyword.starkophone:
            return string
        
        phonetic = ipa_to_latin(string_to_ipa(string, language_code))
        
        starkophone_substring = lambda: levenshtein(keyword.starkophone, get_starkophone(phonetic) or '', 0)
        phonetic_substring = lambda: levenshtein(keyword.simple_phonetic, phonetic, 0.1)
            
        # return starkophone_substring() or phonetic_substring()
        return '' # TODO: back transformation to get original substring
