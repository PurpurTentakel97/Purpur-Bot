import sqlite3
from pathlib import Path
from typing import Any
from typing import Optional
from typing import Self

from pydantic import BaseModel
from sqlalchemy import MetaData
from sqlalchemy import Table
from sqlalchemy import create_engine
from sqlalchemy import insert
from sqlalchemy import select
from sqlalchemy.engine import Engine

from bot.helpers.log import LogLevel
from bot.helpers.log import LogProgram
from bot.helpers.log import log_default
from bot.helpers.log import log_exception

DATABASE_PATH = Path(__file__).parent.parent.parent.parent / "bot.db"


class Database:
    def __init__(self, engine: Engine) -> None:
        self._engine = engine
        self._metadata = MetaData()

    @classmethod
    def create(cls) -> Optional[Self]:
        try:
            engine = create_engine(f"sqlite:///{DATABASE_PATH}")
            return cls(engine)

        except sqlite3.OperationalError:
            log_default(LogLevel.ERROR, "Failed to create the database. Database isn't started.")
            return None

    def close(self) -> None:
        self._engine.dispose()

    # get
    def find_one[T: BaseModel](self, table_name: str, where: dict[str, Any], type_: type[T]) -> Optional[T]:
        try:
            table = Table(table_name, self._metadata, autoload_with=self._engine)
            statement = select(table).filter_by(**where)

            with self._engine.begin() as connection:
                result = connection.execute(statement).mappings().fetchone()

                if result is None:
                    return None

                return type_.model_validate(result)

        except Exception as e:
            log_exception(e, LogProgram.Default, f"Failed to find data in the database. | table: {table_name}")
            return None

    def find_all[T: BaseModel](self, table_name: str, where: dict[str, Any], type_: type[T]) -> list[T]:
        try:
            table = Table(table_name, self._metadata, autoload_with=self._engine)
            statement = select(table).filter_by(**where)

            with self._engine.begin() as connection:
                result = connection.execute(statement).mappings().fetchall()
                return [type_.model_validate(row) for row in result]

        except Exception as e:
            log_exception(e, LogProgram.Default, f"Failed to find data in the database. | table: {table_name}")
            return []

    # store
    def save(self, table_name: str, data: dict[str, Any]) -> bool:
        try:
            table = Table(table_name, self._metadata, autoload_with=self._engine)
            statement = insert(table).values(**data)

            with self._engine.begin() as connection:
                connection.execute(statement)

            return True

        except Exception as e:
            log_exception(e, LogProgram.Default, f"Failed to save data to the database. | table_name: {table_name}")
            return False

    def save_with_returned_id(self, table_name: str, data: dict[str, Any]) -> Optional[int]:
        try:
            table = Table(table_name, self._metadata, autoload_with=self._engine)
            statement = insert(table).values(**data)

            with self._engine.begin() as connection:
                result = connection.execute(statement)
                last_id = result.lastrowid

            return last_id

        except Exception as e:
            log_exception(
                e, LogProgram.Default, f"Failed to save data to the database and return id. | table_name: {table_name}"
            )
            return None

    # update
    def update(self, table_name: str, where: dict[str, Any], data: dict[str, Any]) -> bool:
        try:
            table = Table(table_name, self._metadata, autoload_with=self._engine)
            statement = table.update().filter_by(**where).values(**data)

            with self._engine.begin() as connection:
                connection.execute(statement)
                return True

        except Exception as e:
            log_exception(e, LogProgram.Default, f"Failed to update data in the database. | table_name: {table_name}")
            return False

    # delete
    def delete(self, table_name: str, where: dict[str, Any]) -> bool:
        try:
            table = Table(table_name, self._metadata, autoload_with=self._engine)
            statement = table.delete().filter_by(**where)

            with self._engine.begin() as connection:
                connection.execute(statement)
                return True

        except Exception as e:
            log_exception(e, LogProgram.Default, f"Failed to delete data in the database. | table_name: {table_name}")
            return False
