from collections.abc import Iterable
from dataclasses import dataclass
from typing import Protocol

from stark.tools.common.span import Span

type Metadata = dict[str, object]


@dataclass
class DictionaryItem:
    name: str
    phonetic: str
    simple_phonetic: str
    language_code: str
    metadata: Metadata


@dataclass
class LookupResult:
    span: Span
    item: DictionaryItem
    # item: list[DictionaryItem]


class DictionaryStorageProtocol(Protocol):
    def write_one(self, item: DictionaryItem): ...
    def search_equal_simple_phonetic(
        self, simple_phonetic: str
    ) -> list[DictionaryItem]: ...
    def search_contains_simple_phonetic(
        self, simple_phonetic: str
    ) -> list[DictionaryItem]: ...
    def iterate(self) -> Iterable[DictionaryItem]: ...
    def clear(self): ...
    def search_equal_name(
        self, name: str, language_code: str
    ) -> list[DictionaryItem]: ...
    def search_contains_name(
        self, name: str, language_code: str
    ) -> list[DictionaryItem]: ...
    def get_count(self) -> int: ...
