from __future__ import annotations

import json
import sqlite3

from ..models import DictionaryItem, DictionaryStorageProtocol


class DictionaryStorageSQLite(DictionaryStorageProtocol):
    def __init__(self, sql_url: str):
        self._conn = sqlite3.connect(sql_url, check_same_thread=False)
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS dictionary (
                name TEXT PRIMARY KEY,
                latin TEXT,
                simplephone TEXT,
                metadata TEXT
            )
            """
        )
        self._conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_simplephone ON dictionary(simplephone)
            """
        )
        self._conn.commit()

    def write_one(self, item: DictionaryItem):
        self._conn.execute(
            """
            INSERT OR REPLACE INTO dictionary (name, latin, simplephone, metadata)
            VALUES (?, ?, ?, ?)
            """,
            (item.name, item.latin, item.simplephone, json.dumps(item.metadata)),
        )
        self._conn.commit()

    def search_equal_simple_phonetic(self, simplephone: str) -> list[DictionaryItem]:
        cur = self._conn.execute(
            """
            SELECT name, latin, simplephone, metadata FROM dictionary
            WHERE simplephone = ?
            """,
            (simplephone,),
        )
        rows = cur.fetchall()
        return [
            DictionaryItem(
                name=row[0],
                latin=row[1],
                simplephone=row[2],
                metadata=json.loads(row[3]) if row[3] else {},
            )
            for row in rows
        ]

    def search_contains_simple_phonetic(self, simplephone: str) -> list[DictionaryItem]:
        cur = self._conn.execute(
            """
            SELECT name, latin, simplephone, metadata FROM dictionary
            WHERE simplephone LIKE ?
            """,
            (f"%{simplephone}%",),
        )
        rows = cur.fetchall()
        return [
            DictionaryItem(
                name=row[0],
                latin=row[1],
                simplephone=row[2],
                metadata=json.loads(row[3]) if row[3] else {},
            )
            for row in rows
        ]

    def clear(self) -> None:
        self._conn.execute(
            """
            DELETE FROM dictionary
            """
        )
        self._conn.commit()
