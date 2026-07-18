import logging
import warnings
from pathlib import Path
from typing import Generator

from stark.general.localisation.language_code import LanguageCode

from .localizable_string import LocalizableString
from .strings import StringsFile

logger = logging.getLogger(__name__)

Languages = dict[LanguageCode, StringsFile]


class Localizer:
    languages: set[LanguageCode]
    base_language: LanguageCode
    localizable: Languages
    recognizable: Languages

    def __init__(self, languages: set[LanguageCode] | None = None, base_language: LanguageCode = "en"):
        self.languages = languages or {"en"}
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

    def get_localizable(self, key: str, language: LanguageCode) -> str | None:
        return self._get_string(key, language, self.localizable)

    def get_recognizable(self, key: str, language: LanguageCode) -> str | None:
        return self._get_string(key, language, self.recognizable)

    def load(self):
        self._ensure_strings_dirs()
        self._load_files("localizable", self.localizable)
        self._load_files("recognizable", self.recognizable)

        missing_localizable = self.languages - self.localizable.keys()
        missing_recognizable = self.languages - self.recognizable.keys()

        if missing_localizable or missing_recognizable:
            warnings.warn(
                "Not all languages found in string files."
                + (f"\nMissing localizable: {missing_localizable}" if missing_localizable else "")
                + (f"\nMissing recognizable: {missing_recognizable}" if missing_recognizable else ""),
                RuntimeWarning,
            )

        self._check_completeness(self.localizable)
        self._check_completeness(self.recognizable)

    def verify_recognizable(self, key: str):
        if self.recognizable[self.base_language].get(key) is None:
            warnings.warn(
                f"Recognizable key '{key}' for base language '{self.base_language}' not found. Added key to '{self.recognizable[self.base_language].path}'. Translation needed.",
                RuntimeWarning,
            )
            with open(self.recognizable[self.base_language].path, "a") as f:
                f.write(f'\n{key} = "{key}"')
            return
        for lang in self.languages:
            if self.recognizable[lang].get(key):
                continue
            warnings.warn(
                f"Recognizable key '{key}' for language '{lang}' not found in file '{self.recognizable[lang].path}'.",
                RuntimeWarning,
            )

    def verify_localizable(self, key: str):
        if self.localizable[self.base_language].get(key) is None:
            warnings.warn(
                f"Localizable key '{key}' for base language '{self.base_language}' not found. Added key to '{self.localizable[self.base_language].path}'. Translation needed.",
                RuntimeWarning,
            )
            with open(self.localizable[self.base_language].path, "a") as f:
                f.write(f'\n{key} = "{key}"')
            return
        for lang in self.languages:
            if self.localizable[lang].get(key):
                continue
            warnings.warn(
                f"Localizable key '{key}' for language '{lang}' not found in file '{self.localizable[lang].path}'.",
                RuntimeWarning,
            )

    def _get_string(
        self, key: str, language: LanguageCode, source: Languages, file_name: str = "localizable"
    ) -> str | None:
        if language in source and (result := source[language].get(key)):
            return result
        warnings.warn(
            f"Localizer key '{key}' not found for language '{language}' in {file_name}.",
            RuntimeWarning,
        )
        if self.base_language in source and (result := source[self.base_language].get(key)):
            return result
        if "base" != self.base_language and "base" in source and (result := source["base"].get(key)):
            return result
        warnings.warn(
            f"Localizer key '{key}' not found for base language '{self.base_language}' in {file_name}.",
            RuntimeWarning,
        )
        return None

    def _ensure_strings_dirs(self):
        for lang in self.languages | {"base"}:
            lang_dir = Path("strings") / lang
            lang_dir.mkdir(parents=True, exist_ok=True)
            for filename in ("localizable", "recognizable"):
                filepath = lang_dir / f"{filename}.strings"
                if not filepath.exists():
                    filepath.touch()
                    logger.info(f"Created {filepath}")

    def _load_files(self, name: str, output: Languages):
        for language, strings_file in self._search_files(name):
            if language != "base" and language not in self.languages:
                continue
            strings_file.read()
            output[language] = strings_file
            if language == "base":
                strings_file.language_code = self.base_language

    def _search_files(self, filename: str) -> Generator[tuple[str, StringsFile], None, None]:
        for path in Path(".").rglob(f"strings/*/{filename}.strings"):
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
                    f"Missing keys in {strings_file.path}: {missing}",
                    RuntimeWarning,
                )
