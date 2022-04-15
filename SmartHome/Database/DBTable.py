from __future__ import annotations
from typing import List, Dict, Any, Optional
import sqlite3
from sqlite3 import Error
import traceback

try: from . import config
except ImportError: import config


def eprint(*args, **kwargs):
    if config.sql_exceptions_enabled:
        print(*args, **kwargs)

def lprint(*args, **kwargs):
    if config.sql_logs_enabled:
        print(*args, **kwargs)

def sqlite(func):
    def wrapper(self, *args, **kwargs):
        result = None

        try:
            connect = sqlite3.connect(f'{config.db_name}.sqlite')
            cursor = connect.cursor()

            cursor.execute('pragma foreign_keys = on')
            connect.commit()

            sql_list = []

            def execute(sql: str):
                lprint(f'Execute: "{sql}"')
                sql_list.append(sql)
                return cursor.execute(sql)

            result = func(self, execute, *args, **kwargs)
            connect.commit()

        except Error as e:
            eprint('-'*25, ' ERROR ', '-'*26)
            eprint(f'SQLite error: {" ".join(e.args)}')
            eprint(f'Exception class is: {e.__class__}')
            eprint(f'SQL Request is: "{sql_list.pop()}"')
            eprint(f'\nTraceback: {traceback.format_exc()}')
            eprint('-'*60)
        except Exception as e:
            eprint('-'*23, ' EXCEPTION ', '-'*24)
            eprint(f'Exception args: {" ".join(e.args)}')
            eprint(f'Exception class is {e.__class__}')
            eprint(f'\nTraceback: {traceback.format_exc()}')
            eprint('-'*60)
        finally:
            connect.close()
            return result

    return wrapper


class DBTable:
    table_name: str
    columns: List[str]
    id_type = 'text'

    @classmethod
    @sqlite
    def sql_request(cls, execute, string: str) -> Any:
        return execute(string).fetchall()

    # --------------    Create      ---------------

    @sqlite
    def __init__(self, execute, table_name: str, columns: Dict[str, str]):
        self.table_name = table_name
        if not execute(f'select * from sqlite_master WHERE type = "table" AND name = "{self.table_name}"').fetchall():
            if columns:
                columns_types = ', '.join([f'{name} {args}' for name, args in columns.items()])
                execute(f'create table if not exists {self.table_name}(id {self.id_type} primary key, {columns_types})')
                self.columns = ['id', *columns.keys()]
        else:
            self.columns = [properties[1] for properties in execute(f'pragma table_info({self.table_name})').fetchall()]

    @sqlite
    def create(self, execute, dict: Dict[str, Any]):
        values = [f'"{v}"' for v in dict.values()]
        execute(f'insert into {self.table_name}({", ".join(self.columns)}) values({", ".join(values)})')

    # --------------    Read      ---------------

    def get(self, id: str) -> Optional[Dict[str, Any]]:
        return self.first(where = f'id = "{id}"')

    @sqlite
    def first(self, execute, where: str = '') -> Optional[Dict[str, Any]]:
        if where:
            where = f' where {where}'
        return self._parsedone(execute(f'select * from {self.table_name}{where} limit 1').fetchone())

    @sqlite
    def where(self, execute, condition: str) -> List[Any]:
        return self._parsed(execute(f'select * from {self.table_name} where {condition}').fetchall())

    @sqlite
    def all(self, execute) -> Dict[str, Any]:
        return self._parsed(execute(f'select * from {self.table_name}').fetchall())

    @sqlite
    def count(self, execute) -> int:
        return execute(f'select count(*) from {self.table_name}')

    @sqlite
    def countWhere(self, execute, condition: str) -> int:
        return execute(f'select count(*) from {self.table_name} where {condition}')

    # --------------    Update      ---------------

    @sqlite
    def update(self, execute,  values: Dict[str, Any], id: Optional[Any] = None):
        id = values.get('id') or id
        assert id != None
        updates = ', '.join([f'{key} = "{value}"' for key, value in values.items() if key != 'id'])
        execute(f'update {self.table_name} set {updates} where id = "{id}"')

    @sqlite
    def updateWhere(self, execute, values: Dict[str, Any], where: str):
        updates = " ".join([f'{key} = "{value}"' for key, value in values.items()])
        execute(f'update {self.table_name} set {updates} where {where}')

    # --------------    Delete      ---------------

    @sqlite
    def drop(self, execute):
        execute(f'drop table if exists {self.table_name}')

    @sqlite
    def delete(self, execute, where: str):
        execute(f'delete from {self.table_name} where {where}')

    # --------------    Advanced      ---------------

    @sqlite
    def alter(self, execute, to: DBModel, foreignKey: str, onDelete: str, onUpdate: str):
        execute(f'alter table {self.table_name} add foreign key ({foreignKey}) references {to.table_name}(id) on delete {onDelete} on update {onUpdate}')

    # --------------    Private      -----------------

    def _parsed(self, rows) -> List[Dict[str, Any]]:
        return [self._parsedone(row) for row in rows]

    def _parsedone(self, row) -> Dict[str, Any]:
        dict = {}
        if not row:
            return dict
        for i, value in enumerate(row):
            dict[self.columns[i]] = value
        return dict
