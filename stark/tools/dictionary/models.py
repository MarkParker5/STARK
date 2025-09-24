from typing import Any, Protocol

type Metadata = dict[str, Any]
type Span = tuple[int, int]

from dataclasses import dataclass


@dataclass
class DictionaryItem:
    name: str
    phonetic: str
    simple_phonetic: str
    metadata: Metadata

# @dataclass
# class LookupResult:
#     indices: tuple[int, int]
#     item: 'DictionaryItem'

class DictionaryStorageProtocol(Protocol):
    def write_one(self, item: 'DictionaryItem') -> None: ...
    def search_equal_simple_phonetic(self, simplephone: str) -> list['DictionaryItem']: ...
    def search_contains_simple_phonetic(self, simplephone: str) -> list['DictionaryItem']: ...
    def clear(self) -> None: ...
