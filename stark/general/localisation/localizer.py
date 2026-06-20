from typing import Generator
from pathlib import Path
import warnings
import logging

from .localizable_string import LocalizableString
from .strings import StringsFile


logger = logging.getLogger(__name__)

Languages = dict[str, StringsFile]


class Localizer:

    languages: set[str]
    base_language: str
    localizable: Languages
    recognizable: Languages

    def __init__(self, languages: set[str] | None = None, base_language: str = 'en'):
        self.languages = languages or {'en'}
        self.base_language = base_language
        self.localizable = {}
        self.recognizable = {}

    def localize(self, localizable_string: LocalizableString | str) -> str:
        if not isinstance(localizable_string, LocalizableString):
            return localizable_string
        resolved = self.get_localizable(localizable_string.string, localizable_string.language_code)
        if resolved is None:
            warnings.warn(
                f"Localizer key '{localizable_string.string}' not found for language '{localizable_string.language_code}', using raw key as fallback",
                RuntimeWarning,
            )
            resolved = localizable_string.string
        return resolved.format(**localizable_string.arguments)

    def get_localizable(self, key: str, language: str) -> str | None:
        return self._get_string(key, language, self.localizable)

    def get_recognizable(self, key: str, language: str) -> str | None:
        return self._get_string(key, language, self.recognizable)

    def load(self):
        self._load_files('localizable', self.localizable)
        self._load_files('recognizable', self.recognizable)

        missing_localizable = self.languages - self.localizable.keys()
        missing_recognizable = self.languages - self.recognizable.keys()

        if missing_localizable or missing_recognizable:
            warnings.warn(
                f'Not all languages found in string files.'
                + (f'\nMissing localizable: {missing_localizable}' if missing_localizable else '')
                + (f'\nMissing recognizable: {missing_recognizable}' if missing_recognizable else ''),
                RuntimeWarning,
            )

        self._check_completeness(self.localizable)
        self._check_completeness(self.recognizable)

    def verify_key_exists(self, key: str):
        for lang, strings_file in self.recognizable.items():
            if strings_file.get(key) is not None:
                return
        raise KeyError(f"Localizer key '@{key}' not found in any loaded language. Loaded languages: {set(self.recognizable.keys())}")

    def _get_string(self, key: str, language: str, source: Languages) -> str | None:
        if language in source:
            result = source[language].get(key)
            if result is not None:
                return result
        if 'base' in source:
            return source['base'].get(key)
        return None

    def _load_files(self, name: str, output: Languages):
        for language, strings_file in self._search_files(name):
            if language != 'base' and language not in self.languages:
                continue
            strings_file.read()
            output[language] = strings_file
            if language == 'base':
                strings_file.language_code = self.base_language

    def _search_files(self, filename: str) -> Generator[tuple[str, StringsFile], None, None]:
        for path in Path('.').rglob(f'strings/*/{filename}.strings'):
            language = path.parent.stem
            yield language, StringsFile(path, language)

    def _check_completeness(self, source: Languages):
        if not source:
            return
        all_keys: set[str] = set()
        for strings_file in source.values():
            all_keys.update(strings_file.strings.keys())
        for strings_file in source.values():
            missing = all_keys - set(strings_file.strings.keys())
            if missing:
                warnings.warn(
                    f'Missing keys in {strings_file.path}: {missing}',
                    RuntimeWarning,
                )
