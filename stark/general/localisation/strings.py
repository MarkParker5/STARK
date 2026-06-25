import re
from dataclasses import dataclass
from pathlib import Path

from stark.general.localisation.language_code import LanguageCode


@dataclass
class String:
    key: str
    value: str
    comment: str | None = None


class StringsFile:

    strings: dict[str, String]
    language_code: LanguageCode
    path: Path

    _pattern = re.compile(r'(\/\*(?P<comment>[\s\S]*?)\*\/)?[\s]*"(?P<key>[^"]+)"\s?=\s?"(?P<value>[^"]+)";')

    def __init__(self, path: Path, language_code: LanguageCode):
        self.path = path
        self.language_code = language_code
        self.strings = {}

    def __repr__(self):
        return f'<StringsFile {self.language_code} {len(self.strings)} strings>'

    def get(self, key: str) -> str | None:
        if key in self.strings:
            return self.strings[key].value
        return None

    def read(self):
        with open(self.path, 'r') as f:
            for match in self._pattern.finditer(f.read()):
                groups = match.groupdict()
                if not all([groups.get('value'), groups.get('key')]):
                    continue
                key = groups['key']
                self.strings[key] = String(
                    key=key,
                    value=groups['value'],
                    comment=(groups.get('comment') or '').strip() or None,
                )
