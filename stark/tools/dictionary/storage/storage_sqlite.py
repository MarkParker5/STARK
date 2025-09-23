from __future__ import annotations

import json
import sqlite3

from .models import DictionaryItem, DictionaryStorageProtocol


class DictionaryStorageSQLite(DictionaryStorageProtocol):
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
            (item.name, item.latin, item.starkphone, json.dumps(item.metadata)),
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
                metadata=json.loads(row[3]) if row[3] else {},
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
