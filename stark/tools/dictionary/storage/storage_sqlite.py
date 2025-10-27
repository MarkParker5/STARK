from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterable
import os

from ..models import DictionaryItem, DictionaryStorageProtocol


class DictionaryStorageSQLite(DictionaryStorageProtocol):
    def __init__(self, sql_url: str):
        # ensure its directory exists
        if sql_url != ":memory:":
            # Remove protocol prefix if present (e.g., "sqlite://")
            if "://" in sql_url:
                sql_url = sql_url.split("://", 1)[1]
            dir_path = os.path.dirname(os.path.abspath(sql_url))
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)

        self._conn: sqlite3.Connection = sqlite3.connect(
            sql_url, check_same_thread=False
        )
        _ = self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS dictionary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                phonetic TEXT,
                simple_phonetic TEXT,
                language_code TEXT,
                metadata TEXT
            )
            """
        )
        _ = self._conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_simple_phonetic ON dictionary(simple_phonetic)
            """
        )
        self._conn.commit()

    def write_one(self, item: DictionaryItem):
        _ = self._conn.execute(
            """
            INSERT OR REPLACE INTO dictionary (name, phonetic, simple_phonetic, language_code, metadata)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                item.name,
                item.phonetic,
                item.simple_phonetic,
                item.language_code,
                json.dumps(item.metadata),
            ),
        )
        self._conn.commit()

    def search_equal_name(self, name: str, language_code: str) -> list[DictionaryItem]:
        cur = self._conn.execute(
            """
            SELECT name, phonetic, simple_phonetic, language_code, metadata
            FROM dictionary
            WHERE name = ?
            """,
            (name,),
        )
        return [
            DictionaryItem(
                name=row[0],
                phonetic=row[1],
                simple_phonetic=row[2],
                language_code=row[3],
                metadata=json.loads(row[4]),
            )
            for row in cur.fetchall()
        ]

    def search_contains_name(
        self, name: str, language_code: str
    ) -> list[DictionaryItem]:
        cur = self._conn.execute(
            """
            SELECT name, phonetic, simple_phonetic, language_code, metadata FROM dictionary
            WHERE ? LIKE '%' || name || '%'
            """,
            (name,),
        )
        return [
            DictionaryItem(
                name=row[0],
                phonetic=row[1],
                simple_phonetic=row[2],
                language_code=row[3],
                metadata=json.loads(row[4]),
            )
            for row in cur.fetchall()
        ]

    def search_equal_simple_phonetic(
        self, simple_phonetic: str
    ) -> list[DictionaryItem]:
        cur = self._conn.execute(
            """
            SELECT name, phonetic, simple_phonetic, language_code, metadata FROM dictionary
            WHERE simple_phonetic = ?
            """,
            (simple_phonetic,),
        )
        rows = cur.fetchall()
        return [
            DictionaryItem(
                name=row[0],
                phonetic=row[1],
                simple_phonetic=row[2],
                language_code=row[3],
                metadata=json.loads(row[4]) if row[4] else {},
            )
            for row in rows
        ]

    def search_contains_simple_phonetic(
        self, simple_phonetic: str
    ) -> list[DictionaryItem]:
        cur = self._conn.execute(
            """
            SELECT name, phonetic, simple_phonetic, language_code, metadata FROM dictionary
            WHERE ? LIKE '%' || simple_phonetic || '%'
            """,
            (f"%{simple_phonetic}%",),
        )
        rows = cur.fetchall()
        return [
            DictionaryItem(
                name=row[0],
                phonetic=row[1],
                simple_phonetic=row[2],
                language_code=row[3],
                metadata=json.loads(row[4]) if row[4] else {},
            )
            for row in rows
        ]

    def iterate(self) -> Iterable[DictionaryItem]:
        offset = 0
        page_size = 1000
        while True:
            cur = self._conn.execute(
                """
                SELECT name, phonetic, simple_phonetic, language_code, metadata FROM dictionary
                LIMIT ? OFFSET ?
                """,
                (page_size, offset),
            )
            rows = cur.fetchall()
            if not rows:
                break
            for row in rows:
                yield DictionaryItem(
                    name=row[0],
                    phonetic=row[1],
                    simple_phonetic=row[2],
                    language_code=row[3],
                    metadata=json.loads(row[4]) if row[4] else {},
                )
            offset += page_size

    def clear(self):
        _ = self._conn.execute(
            """
            DELETE FROM dictionary
            """
        )
        self._conn.commit()

    def get_count(self) -> int:
        cur = self._conn.execute(
            """
            SELECT COUNT(*) FROM dictionary
            """
        )
        count = cur.fetchone()[0]
        return count
