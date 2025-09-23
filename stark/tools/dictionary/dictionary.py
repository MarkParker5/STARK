from typing import Any, Dict, Optional

from .models import DictionaryItem, DictionaryStorageProtocol, Metadata


class Dictionary:
    """
    Phonetic-aware dictionary with metadata storage.
    """

    def __init__(self, storage: DictionaryStorageProtocol):
        self.storage = storage
        self._data: Dict[str, Dict[str, Any]] = {}  # id -> {starkphone, origin, metadata}

    # ----------------------
    # Write methods
    # ----------------------
    def write_one(self, name: str, metadata: Optional[Metadata] = None):
        """
        Add a single entry to the dictionary.
        Phonetic conversion happens internally (mandatory).
        """
        latin = ipa2lat(name)
        starkphone_val = starkphone(latin)
        item = DictionaryItem(name=name, latin=latin, starkphone=starkphone_val, metadata=metadata or {})
        self.storage.write_one(item)

    def write_all(self, names: list[tuple[str, Optional[Metadata]]]):
        """
        Add multiple entries in batch. Replaces existing entries.
        """
        self.clear()
        for name, metadata in names:
            self.write_one(name, metadata)

    def clear(self) -> None:
        """
        Clear all entries from the dictionary.
        """
        self.storage.clear()

    # ----------------------
    # Lookup methods
    # ----------------------
    def lookup(self, name_candidate: str) -> list[DictionaryItem]:
        """
        Return best matching entry.
        - Try exact origin match first
        - If collision, use Levenshtein distance on ipa2latin?
        """
        phonetic = starkphone(ipa2lat(name_candidate))
        matches = self.storage.search_equal_starkphone(phonetic)
        if not matches:
            matches = self.storage.search_contains_starkphone(phonetic)
        self._sort_matches(name_candidate, matches)
        # TODO: find a way to also return a span
        return matches

    def check(self, sentence: str) -> list[DictionaryItem]:
        # TODO: implement linear scanning?
        # Can optionally phoneticise entire string, but then backtracking might be lost.
        # Need to solve this.
        # Worst case - linearly check for presence.
        raise NotImplementedError("Not implemented")

    def _sort_matches(self, name_candidate: str, matches: list[DictionaryItem]) -> None:
        # sort by levenshtein distance of strings' latin representations
        matches.sort(key=lambda match: levenshtein(ipa2lat(name_candidate), match.latin))

    # ----------------------
    # Optional / Advanced
    # ----------------------
    async def build(self) -> None:
        """
        Generate a static dictionary at build-time instead of runtime.
        """
        pass

# TODO: add ipa2lat, starkphone, levenshtein
