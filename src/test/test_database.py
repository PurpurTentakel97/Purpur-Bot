from collections.abc import Generator
from pathlib import Path

import pytest
from pydantic import BaseModel
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import MetaData
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from bot.core.types.result import ResultState
from bot.database.database import Database


class MockModel(BaseModel):
    id: int
    name: str


@pytest.fixture
def engine() -> Generator[Engine, None, None]:
    engine = create_engine("sqlite:///:memory:")
    yield engine
    engine.dispose()


@pytest.fixture
def db(engine: Engine) -> Database:
    return Database(engine)


@pytest.fixture
def setup_table(engine: Engine) -> Table:
    metadata = MetaData()
    table = Table(
        "test_table",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("name", String),
    )
    metadata.create_all(engine)
    return table


def test_database_create_success(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    # Mock DATABASE_PATH to a temporary file
    db_path = tmp_path / "test_bot.db"
    monkeypatch.setattr("bot.database.database.DATABASE_PATH", db_path)

    database = Database.create()
    assert database is not None
    assert isinstance(database, Database)
    database.close()


def test_insert_and_select_one(db: Database, setup_table: Table) -> None:
    # Test insert
    data = {"name": "test_name"}
    result = db.insert("test_table", data)
    assert result.state == ResultState.SUCCESS
    assert result.value == 1

    # Test select_one
    select_result = db.select_one("test_table", {"id": 1}, MockModel)
    assert select_result.state == ResultState.SUCCESS
    assert select_result.value is not None
    assert select_result.value.id == 1
    assert select_result.value.name == "test_name"


def test_select_one_no_data(db: Database, setup_table: Table) -> None:
    result = db.select_one("test_table", {"id": 999}, MockModel)
    assert result.state == ResultState.NO_DATA
    assert result.value is None


def test_select_all(db: Database, setup_table: Table) -> None:
    db.insert("test_table", {"name": "name1"})
    db.insert("test_table", {"name": "name2"})

    result = db.select_all("test_table", {}, MockModel)
    assert result.state == ResultState.SUCCESS
    assert result.value is not None
    assert len(result.value) == 2
    assert result.value[0].name == "name1"
    assert result.value[1].name == "name2"


def test_select_all_no_data(db: Database, setup_table: Table) -> None:
    result = db.select_all("test_table", {}, MockModel)
    # The current implementation of select_all in database.py has a bug:
    # result.count == 0 (result is a list of Row objects from fetchall())
    # list doesn't have .count attribute like that (it has .count(value)).
    # It should probably check len(result) == 0.
    # Let's see if it fails.
    assert result.state == ResultState.NO_DATA
    assert result.value == []


def test_update(db: Database, setup_table: Table) -> None:
    db.insert("test_table", {"name": "old_name"})

    update_result = db.update("test_table", {"id": 1}, {"name": "new_name"})
    assert update_result.state == ResultState.SUCCESS

    select_result = db.select_one("test_table", {"id": 1}, MockModel)
    assert select_result.value is not None
    assert select_result.value.name == "new_name"


def test_update_no_data(db: Database, setup_table: Table) -> None:
    update_result = db.update("test_table", {"id": 999}, {"name": "new_name"})
    assert update_result.state == ResultState.NO_DATA


def test_delete(db: Database, setup_table: Table) -> None:
    db.insert("test_table", {"name": "to_delete"})

    delete_result = db.delete("test_table", {"id": 1})
    assert delete_result.state == ResultState.SUCCESS

    select_result = db.select_one("test_table", {"id": 1}, MockModel)
    assert select_result.state == ResultState.NO_DATA


def test_delete_no_data(db: Database, setup_table: Table) -> None:
    delete_result = db.delete("test_table", {"id": 999})
    assert delete_result.state == ResultState.NO_DATA


def test_exception_handling(db: Database) -> None:
    # Pass a non-existent table to trigger an exception
    result = db.select_one("non_existent", {"id": 1}, MockModel)
    assert result.state == ResultState.TYPE_MISSMATCH
    assert result.value is None

    result_all = db.select_all("non_existent", {}, MockModel)
    assert result_all.state == ResultState.TYPE_MISSMATCH
    assert result_all.value == []

    result_insert = db.insert("non_existent", {"name": "test"})
    assert result_insert.state == ResultState.ERROR
    assert result_insert.value is None

    result_update = db.update("non_existent", {"id": 1}, {"name": "test"})
    assert result_update.state == ResultState.ERROR
    assert result_update.value is None

    result_delete = db.delete("non_existent", {"id": 1})
    assert result_delete.state == ResultState.ERROR
    assert result_delete.value is None
