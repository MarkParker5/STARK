from typing import Generator
from pathlib import Path
from .strings import String, StringsFile, FileGroup


Languages = dict[str, StringsFile]

class Localizator:
    
    localizable: Languages
    recognizable: Languages
    languages: set[str]
    
    def __init__(self, languages: set[str]):
        self.languages = languages
        self.localizable = {}
        self.recognizable = {}
        
    def get_localizable(self, key: str, language: str) -> str | None:
        return self._get_string(key, language, self.localizable)
    
    def get_recognizable(self, key: str, language: str) -> str | None:
        return self._get_string(key, language, self.recognizable)
    
    def load(self):
        self._load_files('localizable', self.localizable)
        self._load_files('recognizable', self.recognizable)
        
        assert self.localizable.keys() == self.recognizable.keys() == self.languages, 'Not all languages are found, check the files' + \
            f'\nActive: {self.languages}' + \
            f'\nLocalizable: {self.localizable.keys()}' + \
            f'\nRecognizable: {self.recognizable.keys()}'
        
    # Private
    
    def _get_string(self, key: str, language: str, source: Languages) -> str | None:
        if language not in source:
            return None
        return source[language].get(key)
                
    def _load_files(self, name: str, output: Languages):
        for language, strings_file in self._search_files(name):
            if language in self.languages:
                output[language] = strings_file
                strings_file.read()
        
    def _search_files(self, filename: str) -> Generator[tuple[str, StringsFile], None, None]:
        for path in Path('.').rglob(f'strings/*/{filename}.strings'):
            language = path.parent.stem
            strings_file = StringsFile(path)
            yield language, strings_file
