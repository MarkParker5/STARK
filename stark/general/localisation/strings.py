# https://github.com/MarkParker5/XCodeLocalize/blob/main/src/xcodelocalize/Strings.py

from typing import Optional
from dataclasses import dataclass
from pathlib import Path
import re


@dataclass
class String:
    key: str
    value: str
    comment: Optional[str] = None

@dataclass
class FileGroup:
    directory: str
    filename: str

    @property
    def key(self) -> tuple[str, str]:
        return (self.directory, self.filename)

    def __hash__(self):
        return hash(self.key)

    def __eq__(self, other):
        return self.key == other.key

    def __repr__(self):
        return f'{self.directory}\{self.filename}'

class StringsFile:

    path: Path
    strings: dict[str, String]
    is_read: bool = False

    def __init__(self, path: Path):
        self.path = path
        self.strings = {}

    def __repr__(self):
        if self.is_read:
            return f'<StringsFile with {len(self.strings)} strings>'
        else:
            return f'<StringsFile []>'
        
    def get(self, key: str) -> str | None:
        if key in self.strings:
            return self.strings[key].value
        return None

    def read(self):
        with open(self.path, 'r') as f:
            file = f.read().replace('%@', '_ARG_')

            pattern = re.compile(r'(\/\*(?P<comment>[\s\S]*?)\*\/)?[\s]*"(?P<key>[^"]+)"\s?=\s?"(?P<value>[^"]+)";')

            for match in pattern.finditer(file):
                groups = match.groupdict()

                if not all([groups.get('value'), groups.get('key')]):
                    continue

                key = groups['key']
                value = groups['value']
                comment = groups.get('comment') or ''

                self.strings[key] = String(key, value, comment.strip())
                self.is_read = True

    def save(self):
        with open(self.path, 'w') as f:
            for string in sorted(self.strings.values(), key = lambda s: s.key):
                comment = f'/* {string.comment} */\n' if string.comment else ''
                value = string.value.replace('"', '”')
                f.write(
                    f'\n{comment}"{string.key}" = "{value}";\n' \
                        .replace('_ARG_', '%@') \
                        .replace('$ {','${')
                )
