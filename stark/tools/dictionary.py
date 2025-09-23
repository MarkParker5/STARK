from abc import abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional, Protocol

from stark.general import classproperty

type Metadata = dict[str, Any]
type Span = tuple[int, int]

@dataclass
class DictionaryItem:
    name: str
    latin: str
    starkphone: str
    metadata: Metadata

@dataclass
class LookupResult:
    span: Span
    item: DictionaryItem

class DictionaryStorageProtocol(Protocol):

    def write_one(self, item: DictionaryItem): ...

    def search_equal_starkphone(self, starkphone: str) -> list[DictionaryItem]: ...

    def search_contains_starkphone(self, starkphone: str) -> list[DictionaryItem]: ...

    def clear(self): ...

class DictionaryStorageMemory(DictionaryStorageProtocol):
    def __init__(self):
        self._items: dict[str, DictionaryItem] = {}
        self._phonetic_to_names: dict[str, set[str]] = {}

    def write_one(self, item: DictionaryItem):
        self._items[item.name] = item
        self._phonetic_to_names[item.starkphone].add(item.name)

    def search_equal_starkphone(self, starkphone: str) -> list[DictionaryItem]:
        names = self._phonetic_to_names.get(starkphone, [])
        return [self._items[name] for name in names]

    def search_contains_starkphone(self, starkphone: str) -> list[DictionaryItem]:
        result: list[DictionaryItem] = []
        for key, names in self._phonetic_to_names.items():
            if starkphone in key:
                result.extend(self._items[name] for name in names)
        return result

    def clear(self):
        self._items.clear()
        self._phonetic_to_names.clear()

import sqlite3


class DictionaryStorageSQL(DictionaryStorageProtocol):
    def __init__(self, sql_url: str):
        self._conn = sqlite3.connect(sql_url, check_same_thread=False)
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS dictionary (
                name TEXT PRIMARY KEY,
                latin TEXT,
                starkphone TEXT,
                metadata TEXT
            )
            """
        )
        self._conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_starkphone ON dictionary(starkphone)
            """
        )
        self._conn.commit()

    def write_one(self, item: DictionaryItem):
        self._conn.execute(
            """
            INSERT OR REPLACE INTO dictionary (name, latin, starkphone, metadata)
            VALUES (?, ?, ?, ?)
            """,
            (item.name, item.latin, item.starkphone, repr(item.metadata)),
        )
        self._conn.commit()

    def search_equal_starkphone(self, starkphone: str) -> list[DictionaryItem]:
        cur = self._conn.execute(
            """
            SELECT name, latin, starkphone, metadata FROM dictionary
            WHERE starkphone = ?
            """,
            (starkphone,),
        )
        rows = cur.fetchall()
        return [
            DictionaryItem(
                name=row[0],
                latin=row[1],
                starkphone=row[2],
                metadata=eval(row[3]) if row[3] else {},
            )
            for row in rows
        ]

    def search_contains_starkphone(self, starkphone: str) -> list[DictionaryItem]:
        cur = self._conn.execute(
            """
            SELECT name, latin, starkphone, metadata FROM dictionary
            WHERE starkphone LIKE ?
            """,
            (f"%{starkphone}%",),
        )
        rows = cur.fetchall()
        return [
            DictionaryItem(
                name=row[0],
                latin=row[1],
                starkphone=row[2],
                metadata=eval(row[3]) if row[3] else {},
            )
            for row in rows
        ]

    def clear(self):
        self._conn.execute(
            """
            DELETE FROM dictionary
            """
        )
        self._conn.commit()

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
    def write_one(self, name: Name, metadata: Optional[Metadata] = None):
        """
        Add a single entry to the dictionary.
        Phonetic conversion happens internally (mandatory).
        """
        latin = ipa2lat(name)
        starkphone = starkphone(lat)
        self.storage.write_one(name, latin, starkphone, metadata)

    def write_all(self, names: list[tuple[Name, Metadata | None]]):
        """
        Add multiple entries in batch. Replaces existing entries.
        """
        self.clear()
        for name, metadata in names:
            self.write_one(name, metadata)

    def clear(self):
        """
        Clear all entries from the dictionary.
        """
        self.storage.clear()

    # ----------------------
    # Lookup methods
    # ----------------------
    def lookup(self, name_candidate: str) -> list[DictionaryItem]:
        """
        Returns all matching entries sorted by levenshtein distance of strings' latin representations.
        """
        pass  # TODO: implement exact match + collision resolution
        # TODO: improve single-lang, multilang, and localisation cases
        phonetic = starkphone(ipa2lat(name_candidate))
        matches = self.storage.search_equal_starkphone(phonetic) # O(1) with proper indexing
        if not matches:
            matches = self.storage.search_contains_starkphone(phonetic) # O(n) (probably) where n is the number of entries in the dictionary
        self._sort_matches(name_candidate, matches)
        return matches

    def check(self, sentence: str) -> list[LookupResult]:
        pass  # TODO: implement linear scanning? Can optionally phoneticise entire string, but then backtracking might be lost. Need to solve this. Worst case - linearly check for presence.
        raise NotImplementedError("Not implemented")

    def _sort_matches(self, name_candidate: str, matches: list[LookupResult]):
        # sort by levenshtein distance of strings' latin representations
        matches.sort(key=lambda match: levenshtein(ipa2lat(name_candidate), match.name_latin))

    # ----------------------
    # Optional / Advanced
    # ----------------------
    @abstractmethod
    async def build(self):
        """
        Generate a static dictionary at build-time instead of runtime.
        """
        pass

class NLDictionaryName(NLObject):

    value: list[DictionaryItem]
    dictionary: Dictionary

    @classproperty
    def pattern(cls) -> Pattern:
        return Pattern('**')

    async def did_parse(self, from_string: str):
        if not (matches := self.dictionary.lookup(from_string)):
            raise ParseError(f"Could not find '{from_string}' in dictionary")
        self.value = matches # TODO: options to resolve collisions e.g. best ipa-levenshtein distance
        return from_string

'''
# Simple Usage

# Startup
dictionary = Dictionary(storage=DictionaryStorageMemory())
dictionary.write_one('Nürnberg', {'coords': (49.45, 11.08)})

# Parsing
matches = dictionary.lookup('Nuremberg')
matches[0].metadata # {'coords': (49.45, 11.08)}

matches = dictionary.lookup('Нюрнберг')
matches[0].metadata # {'coords': (49.45, 11.08)}

# Usage via NLDictionaryName Example 1 - plain

class NLExampleDictionaryName(NLDictionaryName):
    dictionary = Dictionary(storage=DictionaryStorageMemory()) # single shared instance
    # NOTE: pattern is **, did_parse is already implemented

NLExampleDictionaryName.dictionary.write_one(...) # fill at startup, update in runtime if needed

# After did_parse, .value of such an object will contain sorted list[DictionaryItem] with the closest match first (at least one always exists).
# if len(matches) > 1, you can just take the first, sort it any other way, or ask the user to choose.

# Usage via NLDictionaryName Example 2 - encapsulated in subclass (preferred)

class MyDictionary(Dictionary):

    def __init__(self):
        # encapsulate db path in custom class
        super().__init__(storage=DictionaryStorageSQL('sqlite:///my-phonetic-dictionary.db'))

    async def build(self):
        # encapsulate filling logic
        # files lookup, db fetch, api requests, etc
        self.write_all(...)

class NLExampleDictionaryName(NLObject):
    dictionary = MyDictionary() # single shared instance of the custom Dictionary subclass

def build_app(): # a single function to build all dictionaries
    NLExampleDictionaryName.dictionary.build() # fill the sqlite file once during the build stage, not at runtime
    SomeOtherDictionary.build()
    # etc
'''
