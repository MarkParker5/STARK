from __future__ import annotations

from collections.abc import Iterable

from ..models import DictionaryItem, DictionaryStorageProtocol


class DictionaryStorageMemory(DictionaryStorageProtocol):
    def __init__(self):
        self._name_to_items: dict[str, DictionaryItem] = {}
        self._simplephone_to_names: dict[str, set[str]] = {}

    def write_one(self, item: DictionaryItem):
        self._name_to_items[item.name] = item
        self._simplephone_to_names.setdefault(item.simple_phonetic, set()).add(
            item.name
        )

    def search_equal_simple_phonetic(
        self, simple_phonetic: str
    ) -> list[DictionaryItem]:
        return [
            self._name_to_items[name]
            for name in self._simplephone_to_names.get(simple_phonetic, set())
        ]

    def search_contains_simple_phonetic(
        self, simple_phonetic: str
    ) -> list[DictionaryItem]:
        return [
            self._name_to_items[name]
            for key, names in self._simplephone_to_names.items()
            if key in simple_phonetic
            for name in names
        ]

    def iterate(self) -> Iterable[DictionaryItem]:
        return iter(self._name_to_items.values())

    def clear(self):
        self._name_to_items.clear()
        self._simplephone_to_names.clear()

    def search_equal_name(self, name: str, language_code: str) -> list[DictionaryItem]:
        item = self._name_to_items.get(name)
        if item:  # and item.language_code == language_code:
            return [item]
        return []

    def search_contains_name(
        self, name: str, language_code: str
    ) -> list[DictionaryItem]:
        return [item for item in self._name_to_items.values() if item.name in name]

    def get_count(self) -> int:
        return len(self._name_to_items)
