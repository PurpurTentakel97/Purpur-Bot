from dataclasses import dataclass
from enum import Enum
from enum import auto
from pathlib import Path
from typing import Final
from typing import final

from pydantic import BaseModel
from pydantic import ValidationError

from bot.helpers.log import LogLevel
from bot.helpers.log import LogProgram
from bot.helpers.log import log_default
from bot.helpers.log import log_exception


@final
class FileResultType(Enum):
    SUCCESS = auto()
    FILE_NOT_FOUND = auto()
    PERMISSION_DENIED = auto()
    IS_A_DIRECTORY = auto()
    INVALID_ENCODING = auto()
    IO_OR_OS_ERROR = auto()
    INVALID_PATH = auto()
    INVALID_DATA = auto()
    TYPE_ERROR = auto()
    VALUE_ERROR = auto()
    RECURSION_ERROR = auto()
    OVERFLOW_ERROR = auto()
    GENERIC = auto()


@dataclass(frozen=True)
class BasicFileResult:
    result_type: FileResultType

    @property
    def success(self) -> bool:
        return self.result_type == FileResultType.SUCCESS


@final
@dataclass(frozen=True)
class LoadJsonResult[T: BaseModel | None](BasicFileResult):
    data: T | None


@final
@dataclass(frozen=True)
class SaveJsonResult(BasicFileResult):
    pass


@final
@dataclass(frozen=True)
class LoadFileResult(BasicFileResult):
    data: str

    def to_json_result[T: BaseModel](self, data: T | None) -> LoadJsonResult[T | None]:
        return LoadJsonResult(self.result_type, data)


@final
@dataclass(frozen=True)
class SaveFileResult(BasicFileResult):
    def to_json_result(self) -> SaveJsonResult:
        return SaveJsonResult(self.result_type)


def load_file(path: Path) -> LoadFileResult:
    if not path.exists():
        log_default(LogLevel.ERROR, f"File {path} does not exist")
        return LoadFileResult(FileResultType.FILE_NOT_FOUND, "")

    if path.is_dir():
        log_default(LogLevel.ERROR, f"File {path} is a directory")
        return LoadFileResult(FileResultType.IS_A_DIRECTORY, "")

    try:
        with open(path, encoding="utf-8") as f:
            data: str = f.read()
            return LoadFileResult(FileResultType.SUCCESS, data)

    except FileNotFoundError as e:
        log_exception(e, LogProgram.Default, "while reading a file")
        return LoadFileResult(FileResultType.FILE_NOT_FOUND, "")
    except PermissionError as e:
        log_exception(e, LogProgram.Default, "while reading a file")
        return LoadFileResult(FileResultType.PERMISSION_DENIED, "")
    except IsADirectoryError as e:
        log_exception(e, LogProgram.Default, "while reading a file")
        return LoadFileResult(FileResultType.IS_A_DIRECTORY, "")
    except UnicodeDecodeError as e:
        log_exception(e, LogProgram.Default, "while reading a file")
        return LoadFileResult(FileResultType.INVALID_ENCODING, "")
    except OSError as e:
        log_exception(e, LogProgram.Default, "while reading a file")
        return LoadFileResult(FileResultType.IO_OR_OS_ERROR, "")

    except Exception as e:
        log_exception(e, LogProgram.Default, "generic error while reading a file")
        return LoadFileResult(FileResultType.GENERIC, "")


def save_file(path: Path, data: str) -> SaveFileResult:
    if path.exists() and path.is_dir():
        log_default(LogLevel.ERROR, f"File {path} is a directory")
        return SaveFileResult(FileResultType.IS_A_DIRECTORY)

    if not path.parent.exists():
        log_default(LogLevel.INFO, f"create directory {path.parent}")
        path.parent.mkdir(parents=True, exist_ok=True)

    if path.exists():
        log_default(LogLevel.INFO, f"overwrite file {path}")
    else:
        log_default(LogLevel.INFO, f"create file {path}")

    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(data)
            return SaveFileResult(FileResultType.SUCCESS)

    except FileNotFoundError as e:
        log_exception(e, LogProgram.Default, "while reading a file")
        return SaveFileResult(FileResultType.FILE_NOT_FOUND)
    except PermissionError as e:
        log_exception(e, LogProgram.Default, "while reading a file")
        return SaveFileResult(FileResultType.PERMISSION_DENIED)
    except IsADirectoryError as e:
        log_exception(e, LogProgram.Default, "while reading a file")
        return SaveFileResult(FileResultType.IS_A_DIRECTORY)
    except UnicodeDecodeError as e:
        log_exception(e, LogProgram.Default, "while reading a file")
        return SaveFileResult(FileResultType.INVALID_ENCODING)
    except OSError as e:
        log_exception(e, LogProgram.Default, "while reading a file")
        return SaveFileResult(FileResultType.IO_OR_OS_ERROR)

    except Exception as e:
        log_exception(e, LogProgram.Default, "unknown error while reading a file")
        return SaveFileResult(FileResultType.GENERIC)


def load_json[T: BaseModel](path: Path, model_class: type[T]) -> LoadJsonResult[T | None]:
    try:
        result: LoadFileResult = load_file(path)
        if not result.success:
            return result.to_json_result(None)

        t: Final = model_class.model_validate_json(result.data)
        return result.to_json_result(t)
    except ValidationError as e:
        log_exception(e, LogProgram.Default, "while loading a JSON")
        return LoadJsonResult(FileResultType.INVALID_DATA, None)


def save_json(path: Path, data: BaseModel) -> SaveJsonResult:
    try:
        result: SaveFileResult = save_file(path, data.model_dump_json(indent=4))
        return result.to_json_result()

    except TypeError as e:
        log_exception(e, LogProgram.Default, "type error while dumping a JSON")
        return SaveJsonResult(FileResultType.INVALID_DATA)
    except RecursionError as e:
        log_exception(e, LogProgram.Default, "recursion error while dumping a JSON")
        return SaveJsonResult(FileResultType.RECURSION_ERROR)
    except OverflowError as e:
        log_exception(e, LogProgram.Default, "overflow error while dumping a JSON")
        return SaveJsonResult(FileResultType.OVERFLOW_ERROR)
    except ValueError as e:
        log_exception(e, LogProgram.Default, "value error while dumping a JSON")
        return SaveJsonResult(FileResultType.VALUE_ERROR)
