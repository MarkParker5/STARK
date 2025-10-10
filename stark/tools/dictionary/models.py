from dataclasses import dataclass
from typing import Any, Iterable, Protocol

from stark.tools.levenshtein import Span

type Metadata = dict[str, Any]

@dataclass
class DictionaryItem:
    name: str
    phonetic: str
    simple_phonetic: str
    metadata: Metadata

@dataclass
class LookupResult:
    span: Span
    item: DictionaryItem
    # item: list[DictionaryItem]

class DictionaryStorageProtocol(Protocol):
    def write_one(self, item: 'DictionaryItem') -> None: ...
    def search_equal_simple_phonetic(self, simplephone: str) -> list['DictionaryItem']: ...
    def search_contains_simple_phonetic(self, simplephone: str) -> list['DictionaryItem']: ...
    def iterate(self) -> Iterable['DictionaryItem']: ...
    def clear(self) -> None: ...
