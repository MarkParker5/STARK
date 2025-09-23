from typing import Any, Protocol

type Metadata = dict[str, Any]
type Span = tuple[int, int]

from dataclasses import dataclass


@dataclass
class DictionaryItem:
    name: str
    latin: str
    starkphone: str
    metadata: Metadata

# @dataclass
# class LookupResult:
#     span: Span
#     item: 'DictionaryItem'

class DictionaryStorageProtocol(Protocol):
    def write_one(self, item: 'DictionaryItem') -> None: ...
    def search_equal_starkphone(self, starkphone: str) -> list['DictionaryItem']: ...
    def search_contains_starkphone(self, starkphone: str) -> list['DictionaryItem']: ...
    def clear(self) -> None: ...
