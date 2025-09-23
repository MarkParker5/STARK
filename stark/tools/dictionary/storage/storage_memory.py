from __future__ import annotations

from .models import DictionaryItem, DictionaryStorageProtocol


class DictionaryStorageMemory(DictionaryStorageProtocol):
    def __init__(self) -> None:
        self._items: dict[str, DictionaryItem] = {}
        self._phonetic_to_names: dict[str, set[str]] = {}

    def write_one(self, item: DictionaryItem):
        self._items[item.name] = item
        self._phonetic_to_names.setdefault(item.starkphone, set()).add(item.name)

    def search_equal_starkphone(self, starkphone: str) -> list[DictionaryItem]:
        return [self._items[name] for name in self._phonetic_to_names.get(starkphone, set())]

    def search_contains_starkphone(self, starkphone: str) -> list[DictionaryItem]:
        result: list[DictionaryItem] = []
        for key, names in self._phonetic_to_names.items():
            if starkphone in key:
                result.extend(self._items[name] for name in names)
        return result

    def clear(self) -> None:
        self._items.clear()
        self._phonetic_to_names.clear()
