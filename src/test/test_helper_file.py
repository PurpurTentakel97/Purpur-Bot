from pathlib import Path
from unittest.mock import MagicMock

from pydantic import BaseModel

from bot.helpers.file import FileResultType
from bot.helpers.file import load_file
from bot.helpers.file import save_file
from bot.helpers.file import load_json
from bot.helpers.file import save_json


class MockModel(BaseModel):
    name: str
    age: int


def test_load_file_success(tmp_path: Path) -> None:
    file_path = tmp_path / "test.txt"
    content = "hello world"
    file_path.write_text(content, encoding="utf-8")

    result = load_file(file_path)

    assert result.success
    assert result.result_type == FileResultType.SUCCESS
    assert result.data == content


def test_load_file_not_found(tmp_path: Path) -> None:
    file_path = tmp_path / "non_existent.txt"

    result = load_file(file_path)

    assert not result.success
    assert result.result_type == FileResultType.FILE_NOT_FOUND
    assert result.data == ""


def test_load_file_is_directory(tmp_path: Path) -> None:
    dir_path = tmp_path / "test_dir"
    dir_path.mkdir()

    result = load_file(dir_path)

    assert not result.success
    assert result.result_type == FileResultType.IS_A_DIRECTORY
    assert result.data == ""


def test_save_file_success(tmp_path: Path) -> None:
    file_path = tmp_path / "save_test.txt"
    content = "save content"

    result = save_file(file_path, content)

    assert result.success
    assert result.result_type == FileResultType.SUCCESS
    assert file_path.read_text(encoding="utf-8") == content


def test_save_file_overwrite(tmp_path: Path) -> None:
    file_path = tmp_path / "overwrite_test.txt"
    file_path.write_text("old content", encoding="utf-8")
    new_content = "new content"

    result = save_file(file_path, new_content)

    assert result.success
    assert file_path.read_text(encoding="utf-8") == new_content


def test_save_file_create_dirs(tmp_path: Path) -> None:
    file_path = tmp_path / "subdir" / "nested" / "file.txt"
    content = "nested content"

    result = save_file(file_path, content)

    assert result.success
    assert file_path.exists()
    assert file_path.read_text(encoding="utf-8") == content


def test_save_file_is_directory(tmp_path: Path) -> None:
    dir_path = tmp_path / "save_dir"
    dir_path.mkdir()

    result = save_file(dir_path, "some data")

    assert not result.success
    assert result.result_type == FileResultType.IS_A_DIRECTORY


def test_load_json_success(tmp_path: Path) -> None:
    file_path = tmp_path / "test.json"
    content = '{"name": "test", "age": 42}'
    file_path.write_text(content, encoding="utf-8")

    result = load_json(file_path, MockModel)

    assert result.success
    assert result.result_type == FileResultType.SUCCESS
    assert result.data is not None
    assert result.data.name == "test"
    assert result.data.age == 42


def test_load_json_not_found(tmp_path: Path) -> None:
    file_path = tmp_path / "non_existent.json"

    result = load_json(file_path, MockModel)

    assert not result.success
    assert result.result_type == FileResultType.FILE_NOT_FOUND
    assert result.data is None


def test_load_json_invalid_data(tmp_path: Path) -> None:
    file_path = tmp_path / "invalid.json"
    content = '{"name": "test"}'  # Missing "age"
    file_path.write_text(content, encoding="utf-8")

    result = load_json(file_path, MockModel)

    assert not result.success
    assert result.result_type == FileResultType.INVALID_DATA
    assert result.data is None


def test_save_json_success(tmp_path: Path) -> None:
    file_path = tmp_path / "save.json"
    data = MockModel(name="save_test", age=100)

    result = save_json(file_path, data)

    assert result.success
    assert result.result_type == FileResultType.SUCCESS
    assert file_path.exists()
    assert '"name":"save_test"' in file_path.read_text(encoding="utf-8")
    assert '"age":100' in file_path.read_text(encoding="utf-8")


def test_save_json_is_directory(tmp_path: Path) -> None:
    dir_path = tmp_path / "save_dir"
    dir_path.mkdir()
    data = MockModel(name="test", age=1)

    result = save_json(dir_path, data)

    assert not result.success
    assert result.result_type == FileResultType.IS_A_DIRECTORY


def test_save_json_type_error() -> None:
    path = Path("dummy.json")
    data = MagicMock(spec=BaseModel)
    data.model_dump_json.side_effect = TypeError("Mocked type error")

    result = save_json(path, data)

    assert not result.success
    assert result.result_type == FileResultType.INVALID_DATA


def test_save_json_recursion_error() -> None:
    path = Path("dummy.json")
    data = MagicMock(spec=BaseModel)
    data.model_dump_json.side_effect = RecursionError("Mocked recursion error")

    result = save_json(path, data)

    assert not result.success
    assert result.result_type == FileResultType.RECURSION_ERROR


def test_save_json_overflow_error() -> None:
    path = Path("dummy.json")
    data = MagicMock(spec=BaseModel)
    data.model_dump_json.side_effect = OverflowError("Mocked overflow error")

    result = save_json(path, data)

    assert not result.success
    assert result.result_type == FileResultType.OVERFLOW_ERROR


def test_save_json_value_error() -> None:
    path = Path("dummy.json")
    data = MagicMock(spec=BaseModel)
    data.model_dump_json.side_effect = ValueError("Mocked value error")

    result = save_json(path, data)

    assert not result.success
    assert result.result_type == FileResultType.VALUE_ERROR
