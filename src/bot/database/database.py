import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from typing import Optional
from typing import final

DATABASE_PATH = Path.cwd() / "bot.db"


@final
@dataclass(frozen=True)
class DatabaseSaveData:
    table_name: str
    data: dict[str, Any]


@final
@dataclass(frozen=True)
class DatabaseUpdateData:
    table_name: str
    data: dict[str, Any]
    where: dict[str, Any]


@final
@dataclass(frozen=True)
class DatabaseDeleteData:
    table_name: str
    where: dict[str, Any]


@final
@dataclass(frozen=True)
class DatabaseGetData:
    table_name: str
    keys: list[str]
    where: dict[str, Any]


@final
class Database:
    def __init__(self) -> None:
        self._connection = sqlite3.connect(DATABASE_PATH)
        self._cursor = self._connection.cursor()

    def save(self, data: DatabaseSaveData) -> None:
        keys = list(data.data.keys())
        values = tuple(data.data.values())

        name_clause = ", ".join(keys)
        value_clause = ", ".join(["?"] * len(keys))
        command = f"INSERT INTO {data.table_name} ({name_clause}) VALUES ({value_clause})"

        self._cursor.execute(command, values)
        self._connection.commit()

    def update(self, data: DatabaseUpdateData) -> None:
        data_keys = list(data.data.keys())
        data_values = tuple(data.data.values())
        where_keys = list(data.where.keys())
        where_values = tuple(data.where.values())

        set_clause = ", ".join([f"{key} = ?" for key in data_keys])
        where_clause = " AND ".join([f"{key} = ?" for key in where_keys])
        command = f"UPDATE {data.table_name} SET {set_clause} WHERE {where_clause}"

        self._cursor.execute(command, data_values + where_values)
        self._connection.commit()

    def delete(self, data: DatabaseDeleteData) -> None:
        keys = list(data.where.keys())
        values = tuple(data.where.values())

        where_clause = " AND ".join([f"{key} = ?" for key in keys])
        command = f"DELETE FROM {data.table_name} WHERE {where_clause}"

        self._cursor.execute(command, values)
        self._connection.commit()

    def get_single[T](self, data: DatabaseGetData, return_type: T) -> Optional[T]:
        where_keys = list(data.where.keys())
        where_values = tuple(data.where.values())

        keys_claus = ", ".join(data.keys)
        where_clause = " AND ".join([f"{key} = ?" for key in where_keys])
        command = f"SELECT {keys_claus} FROM {data.table_name} WHERE {where_clause} LIMIT 1"

        self._cursor.execute(command, where_values)
        fetch_result = self._cursor.fetchone()

        if fetch_result is None:
            return None

        value = fetch_result[0]

        if isinstance(value, type(return_type)):
            return value

        return None


DATABASE = Database()
