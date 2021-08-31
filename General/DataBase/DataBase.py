import sqlite3
from sqlite3 import Error
import config

def sqlite(func):
    def wrapper(self, *args):
        result = None
        try:
            connect = sqlite3.connect(config.db_name)
            cursor  = connect.cursor()
            result = func(self, cursor, *args)
            connect.commit()
        except Error as er:
            print('SQLite error: %s' % (' '.join(er.args)))
            print("Exception class is: ", er.__class__)
            print('SQLite traceback: ')
        finally:
            connect.close()
            return result

    return wrapper

class DataBase:
    @sqlite
    def __init__(self, cursor, table_name, columns = None):
        self.table_name = table_name
        if not cursor.execute(f'select * from sqlite_master WHERE type = "table" AND name = "{self.table_name}"').fetchall():
            if columns:
                cursor.execute(f'create table if not exists {self.table_name}(id integer PRIMARY KEY, {", ".join(columns)})')
                self.columns = ['id',]+columns
        else:
            self.columns = [properties[1] for properties in cursor.execute(f'pragma table_info({self.table_name})').fetchall()]


    @sqlite
    def all(self, cursor):
        rows = cursor.execute(f'select * from {self.table_name}').fetchall()
        data = []
        for row in rows:
            dict = {}
            for i, value in enumerate(row):
                dict[self.columns[i]] = value
            data.append(dict)
        return data

    @sqlite
    def where(self, cursor, condition):
        return cursor.execute(f'select * from {self.table_name} where {condition}')

    @sqlite
    def count(self, count):
        return len(self.all())

    @sqlite
    def update(self, cursor, values, where):
        updates = " ".join([f'{key} = "{value}"' for key, value in values.items()])
        cursor.execute(f'update {self.table_name} set {updates} where {where}')

    @sqlite
    def insert(self, cursor, values):
        values = ['"'+v+'"' for v in values]
        cursor.execute(f'insert into {self.table_name}({", ".join(self.columns[1:])}) values({", ".join(values)})')

    @sqlite
    def drop(self, cursor):
        cursor.execute(f'drop table if exists {self.table_name}')
