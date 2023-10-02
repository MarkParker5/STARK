from typing import Generator
from pathlib import Path
import warnings
import re
from .strings import String, StringsFile, FileGroup
from stark.models.localizable_string import LocalizableString


Languages = dict[str, StringsFile]

class Localizer:
    
    localizable: Languages
    recognizable: Languages
    languages: set[str]
    base_language: str # language of the base.strings file
    
    def __init__(self, languages: set[str] | None = None, base_language: str = 'en'):
        self.languages = languages or {'en'}
        self.base_language = base_language
        self.localizable = {}
        self.recognizable = {}
        
    def localize(self, localizable_string: LocalizableString | str) -> str:
        if not isinstance(localizable_string, LocalizableString):
            return localizable_string
        
        string = self.get_localizable(localizable_string.string, localizable_string.language_code) or localizable_string.string
        
        return string.format(**localizable_string.arguments)
        
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
            
        self.check(self.localizable)
        
    def check(self, source: Languages):
        first = next(iter(source.values()))
        all_keys = set(first.strings.keys())
        
        for strings_file in source.values():
            all_keys.update(strings_file.strings.keys())
            
        for strings_file in source.values():
            if all_keys != set(strings_file.strings.keys()):
                warnings.warn(
                    f'Not all keys are present in strings files, check the files' \
                    + f'\nFile: {strings_file.path}' \
                    + f'\nKeys: {all_keys - set(strings_file.strings.keys())}',
                    RuntimeWarning
                )

    # Private
    
    def _get_string(self, key: str, language: str, source: Languages) -> str | None:
        if language not in source:
            return None
        return source[language].get(key) or source['base'].get(key)
                
    def _load_files(self, name: str, output: Languages):
        for language, strings_file in self._search_files(name):
            if not language in self.languages: 
                continue
            output[language] = strings_file
            strings_file.read()
            
            if language == 'base':
                strings_file.is_base = True
                strings_file.language_code = self.base_language
        
    def _search_files(self, filename: str) -> Generator[tuple[str, StringsFile], None, None]:
        for path in Path('.').rglob(f'strings/*/{filename}.strings'):
            language = path.parent.stem
            strings_file = StringsFile(path, language)
            yield language, strings_file
