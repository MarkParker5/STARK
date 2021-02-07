import sqlite3
from sqlite3 import Error
import config

def sqlite(func):
    def wrapper(this, *args):
        result = None
        try:
            connect = sqlite3.connect(config.db_name)
            cursor  = connect.cursor()
            result = func(this, cursor, *args)
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
    def __init__(this, cursor, table_name, columns = None):
        this.table_name = table_name
        if not cursor.execute(f'select * from sqlite_master WHERE type = "table" AND name = "{this.table_name}"').fetchall():
            if columns:
                cursor.execute(f'create table if not exists {this.table_name}(id integer PRIMARY KEY, {", ".join(columns)})')
                this.columns = ['id',]+columns
        else:
            this.columns = [properties[1] for properties in cursor.execute(f'pragma table_info({this.table_name})').fetchall()]


    @sqlite
    def all(this, cursor):
        rows = cursor.execute(f'select * from {this.table_name}').fetchall()
        data = []
        for row in rows:
            dict = {}
            for i, value in enumerate(row):
                dict[this.columns[i]] = value
            data.append(dict)
        return data

    @sqlite
    def where(this, cursor, condition):
        return cursor.execute(f'select * from {this.table_name} where {condition}')

    @sqlite
    def count(this, count):
        return len(this.all())

    @sqlite
    def update(this, cursor, values, where):
        updates = " ".join([f'{key} = "{value}"' for key, value in values.items()])
        cursor.execute(f'update {this.table_name} set {updates} where {where}')

    @sqlite
    def insert(this, cursor, values):
        values = ['"'+v+'"' for v in values]
        cursor.execute(f'insert into {this.table_name}({", ".join(this.columns[1:])}) values({", ".join(values)})')

    @sqlite
    def drop(this, cursor):
        cursor.execute(f'drop table if exists {this.table_name}')
