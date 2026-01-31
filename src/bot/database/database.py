import sqlite3
from pathlib import Path
from typing import Any
from typing import Optional
from typing import Self

from pydantic import BaseModel
from sqlalchemy import MetaData
from sqlalchemy import Table
from sqlalchemy import create_engine
from sqlalchemy import event
from sqlalchemy import insert
from sqlalchemy import select
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError

from bot.core.types.result import Result
from bot.core.types.result import ResultState
from bot.helpers.log import LogLevel
from bot.helpers.log import LogProgram
from bot.helpers.log import log_default
from bot.helpers.log import log_exception

DATABASE_PATH = Path(__file__).parent.parent.parent.parent / "data" / "bot.db"


class Database:
    def __init__(self, engine: Engine) -> None:
        self._engine = engine
        self._metadata = MetaData()

    # core
    @classmethod
    def create(cls) -> Optional[Self]:
        try:
            engine = create_engine(f"sqlite:///{DATABASE_PATH}")

            @event.listens_for(engine, "connect")
            def set_sqlite_pragma(dbapi_connection: Any, connection_record: Any) -> None:  # pyright: ignore [reportUnusedFunction]
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()

            return cls(engine)

        except sqlite3.OperationalError:
            log_default(LogLevel.ERROR, "Failed to create the database. Database isn't started.")
            return None

    def close(self) -> None:
        self._engine.dispose()

    # operations
    def select_one[T: BaseModel](self, table_name: str, where: dict[str, Any], type_: type[T]) -> Result[T]:
        try:
            table = Table(table_name, self._metadata, extend_existing=True, autoload_with=self._engine)
            statement = select(table).filter_by(**where)

            with self._engine.begin() as connection:
                result = connection.execute(statement).mappings().fetchone()

                if result is None:
                    return Result(ResultState.NO_DATA)

                return Result(ResultState.SUCCESS, type_.model_validate(result))

        except Exception as e:
            log_exception(e, LogProgram.Default, f"Failed to find data in the database. | table: {table_name}")
            return Result(ResultState.TYPE_MISSMATCH, None)

    def select_all[T: BaseModel](self, table_name: str, where: dict[str, Any], type_: type[T]) -> Result[list[T]]:
        try:
            table = Table(table_name, self._metadata, extend_existing=True, autoload_with=self._engine)
            statement = select(table).filter_by(**where)

            with self._engine.begin() as connection:
                result = connection.execute(statement).mappings().fetchall()
                if len(result) == 0:
                    return Result(ResultState.NO_DATA, [])
                return Result(ResultState.SUCCESS, [type_.model_validate(row) for row in result])

        except Exception as e:
            log_exception(e, LogProgram.Default, f"Failed to find data in the database. | table: {table_name}")
            return Result(ResultState.TYPE_MISSMATCH, [])

    def insert(self, table_name: str, data: dict[str, Any]) -> Result[int]:
        try:
            table = Table(table_name, self._metadata, extend_existing=True, autoload_with=self._engine)
            statement = insert(table).values(**data)

            with self._engine.begin() as connection:
                result = connection.execute(statement)
                last_id = result.lastrowid

            return Result(ResultState.SUCCESS, last_id)

        except IntegrityError:
            return Result(ResultState.ALREADY_EXISTS, None)

        except Exception as e:
            log_exception(
                e, LogProgram.Default, f"Failed to save data to the database and return id. | table_name: {table_name}"
            )
            return Result(ResultState.ERROR, None)

    def update(self, table_name: str, where: dict[str, Any], data: dict[str, Any]) -> Result[None]:
        try:
            table = Table(table_name, self._metadata, extend_existing=True, autoload_with=self._engine)
            statement = table.update().filter_by(**where).values(**data)

            with self._engine.begin() as connection:
                result = connection.execute(statement)

            return Result(ResultState.SUCCESS if result.rowcount != 0 else ResultState.NO_DATA, None)

        except IntegrityError:
            return Result(ResultState.ALREADY_EXISTS, None)

        except Exception as e:
            log_exception(e, LogProgram.Default, f"Failed to update data in the database. | table_name: {table_name}")
            return Result(ResultState.ERROR, None)

    def delete(self, table_name: str, where: dict[str, Any]) -> Result[None]:
        try:
            table = Table(table_name, self._metadata, extend_existing=True, autoload_with=self._engine)
            statement = table.delete().filter_by(**where)

            with self._engine.begin() as connection:
                result = connection.execute(statement)

            return Result(ResultState.SUCCESS if result.rowcount != 0 else ResultState.NO_DATA, None)

        except Exception as e:
            log_exception(e, LogProgram.Default, f"Failed to delete data in the database. | table_name: {table_name}")
            return Result(ResultState.ERROR, None)
