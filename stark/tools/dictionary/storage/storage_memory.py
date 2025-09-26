from __future__ import annotations

from ..models import DictionaryItem, DictionaryStorageProtocol


class DictionaryStorageMemory(DictionaryStorageProtocol):
    def __init__(self) -> None:
        self._name_to_items: dict[str, DictionaryItem] = {}
        self.__simple_phonetic_to_names: dict[str, set[str]] = {}

    def write_one(self, item: DictionaryItem):
        self._name_to_items[item.name] = item
        self.__simple_phonetic_to_names.setdefault(item.simple_phonetic, set()).add(item.name)

    def search_equal_simple_phonetic(self, simple_phonetic: str) -> list[DictionaryItem]:
        return [self._name_to_items[name] for name in self.__simple_phonetic_to_names.get(simple_phonetic, set())]

    def search_contains_simple_phonetic(self, simple_phonetic: str) -> list[DictionaryItem]:
        result: list[DictionaryItem] = []
        for key, names in self.__simple_phonetic_to_names.items():
            if key in simple_phonetic:
                result.extend(self._name_to_items[name] for name in names)
        return result

    def clear(self) -> None:
        self._name_to_items.clear()
        self.__simple_phonetic_to_names.clear()
