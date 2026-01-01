import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from typing import Optional
from typing import Self
from typing import final

from bot.helpers.log import LogLevel
from bot.helpers.log import log_default
from bot.types.database_result import DatabaseResult

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
@dataclass(frozen=True)
class SingleDatabaseResult[T]:
    data: T
    result: DatabaseResult


@final
class Database:
    def __init__(self, connection: sqlite3.Connection, cursor: sqlite3.Cursor) -> None:
        self._connection = connection
        self._cursor = cursor

    @classmethod
    def create(cls) -> Optional[Self]:
        try:
            connection = sqlite3.connect(DATABASE_PATH)
            cursor = connection.cursor()
            return cls(connection, cursor)
        except sqlite3.Error as e:
            log_default(LogLevel.ERROR, f"Failed to connect to database: {e}")
            return None

    def close(self) -> None:
        self._cursor.close()
        self._connection.close()

    def save(self, data: DatabaseSaveData) -> DatabaseResult:
        keys = list(data.data.keys())
        values = tuple(data.data.values())

        name_clause = ", ".join(keys)
        value_clause = ", ".join(["?"] * len(keys))
        command = f"INSERT INTO {data.table_name} ({name_clause}) VALUES ({value_clause})"

        try:
            self._cursor.execute(command, values)
            self._connection.commit()
        except sqlite3.Error as e:
            log_default(LogLevel.ERROR, f"Error while storing data to the database. {e}")
            return DatabaseResult.ERROR

        return DatabaseResult.SUCCESS

    def update(self, data: DatabaseUpdateData) -> DatabaseResult:
        data_keys = list(data.data.keys())
        data_values = tuple(data.data.values())
        where_keys = list(data.where.keys())
        where_values = tuple(data.where.values())

        set_clause = ", ".join([f"{key} = ?" for key in data_keys])
        where_clause = " AND ".join([f"{key} = ?" for key in where_keys])
        command = f"UPDATE {data.table_name} SET {set_clause} WHERE {where_clause}"

        try:
            self._cursor.execute(command, data_values + where_values)
            self._connection.commit()

            if self._cursor.rowcount == 0:
                return DatabaseResult.NO_DATA_EDITED

        except sqlite3.Error as e:
            log_default(LogLevel.ERROR, f"Error while updating data in the database. {e}")
            return DatabaseResult.ERROR

        return DatabaseResult.SUCCESS

    def delete(self, data: DatabaseDeleteData) -> DatabaseResult:
        keys = list(data.where.keys())
        values = tuple(data.where.values())

        where_clause = " AND ".join([f"{key} = ?" for key in keys])
        command = f"DELETE FROM {data.table_name} WHERE {where_clause}"

        try:
            self._cursor.execute(command, values)
            self._connection.commit()

            if self._cursor.rowcount == 0:
                return DatabaseResult.NO_DATA_EDITED

        except sqlite3.Error as e:
            log_default(LogLevel.ERROR, f"Error while deleting data from the database. {e}")
            return DatabaseResult.ERROR

        return DatabaseResult.SUCCESS

    def get_single[T](self, data: DatabaseGetData, return_type: T) -> SingleDatabaseResult[T | None]:
        where_keys = list(data.where.keys())
        where_values = tuple(data.where.values())

        keys_claus = ", ".join(data.keys)
        where_clause = " AND ".join([f"{key} = ?" for key in where_keys])
        command = f"SELECT {keys_claus} FROM {data.table_name} WHERE {where_clause} LIMIT 1"

        try:
            self._cursor.execute(command, where_values)
            fetch_result = self._cursor.fetchone()
        except sqlite3.Error as e:
            log_default(LogLevel.ERROR, f"Error while fetching data from the database. {e}")
            return SingleDatabaseResult(None, DatabaseResult.ERROR)

        if fetch_result is None:
            log_default(LogLevel.INFO, f"No data found in table {data.table_name} | Query: {command}")
            return SingleDatabaseResult(None, DatabaseResult.EMPTY)

        value = fetch_result[0]

        if not isinstance(value, type(return_type)):
            return SingleDatabaseResult(None, DatabaseResult.TYPE_MISSMATCH)

        return SingleDatabaseResult(value, DatabaseResult.SUCCESS)
