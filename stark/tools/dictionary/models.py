from dataclasses import dataclass
from typing import Any, NamedTuple, Protocol

type Metadata = dict[str, Any]

class Span(NamedTuple):
    start: int
    end: int

@dataclass
class DictionaryItem:
    name: str
    phonetic: str
    simple_phonetic: str
    metadata: Metadata

@dataclass
class LookupResult:
    indices: Span
    item: list[DictionaryItem]

class DictionaryStorageProtocol(Protocol):
    def write_one(self, item: 'DictionaryItem') -> None: ...
    def search_equal_simple_phonetic(self, simplephone: str) -> list['DictionaryItem']: ...
    def search_contains_simple_phonetic(self, simplephone: str) -> list['DictionaryItem']: ...
    def clear(self) -> None: ...
