import json
from dataclasses import dataclass
from enum import Enum
from enum import auto
from pathlib import Path
from typing import final

from src.helpers.log import LogLevel
from src.helpers.log import LogProgram
from src.helpers.log import log_default
from src.helpers.log import log_exception
from src.helpers.my_types import JsonDict


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
class LoadJsonResult(BasicFileResult):
    data: JsonDict


@final
@dataclass(frozen=True)
class SaveJsonResult(BasicFileResult):
    pass


@final
@dataclass(frozen=True)
class LoadFileResult(BasicFileResult):
    data: str

    def to_json_result(self, data: JsonDict) -> LoadJsonResult:
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


def load_json(path: Path) -> LoadJsonResult:
    try:
        result: LoadFileResult = load_file(path)
        if not result.success:
            return result.to_json_result({})
        data: JsonDict = json.loads(result.data)
        return result.to_json_result(data)

    except json.JSONDecodeError as e:
        log_exception(e, LogProgram.Default, "while loading a JSON")
        return LoadJsonResult(FileResultType.INVALID_ENCODING, {})
    except RecursionError as e:
        log_exception(e, LogProgram.Default, "while loading a JSON")
        return LoadJsonResult(FileResultType.RECURSION_ERROR, {})
    except OverflowError as e:
        log_exception(e, LogProgram.Default, "while loading a JSON")
        return LoadJsonResult(FileResultType.OVERFLOW_ERROR, {})

    except Exception as e:
        log_exception(e, LogProgram.Default, "unknown error while loading a JSON")
        return LoadJsonResult(FileResultType.GENERIC, {})


def save_json(path: Path, data: JsonDict) -> SaveJsonResult:
    try:
        result: SaveFileResult = save_file(path, json.dumps(data, indent=4))
        return result.to_json_result()

    except TypeError as e:
        log_exception(e, LogProgram.Default, "while dumping a JSON")
        return SaveJsonResult(FileResultType.TYPE_ERROR)
    except ValueError as e:
        log_exception(e, LogProgram.Default, "while dumping a JSON")
        return SaveJsonResult(FileResultType.VALUE_ERROR)
    except RecursionError as e:
        log_exception(e, LogProgram.Default, "while dumping a JSON")
        return SaveJsonResult(FileResultType.RECURSION_ERROR)
    except OverflowError as e:
        log_exception(e, LogProgram.Default, "while dumping a JSON")
        return SaveJsonResult(FileResultType.OVERFLOW_ERROR)

    except Exception as e:
        log_exception(e, LogProgram.Default, "unknown error while dumping a JSON")
        return SaveJsonResult(FileResultType.GENERIC)
