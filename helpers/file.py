import json
from enum import Enum, auto
from pathlib import Path

from helpers.log import LogLevel, log, log_exception


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


class BasicFileResult:
    def __init__(self, result_type: FileResultType) -> None:
        self._result_type: FileResultType = result_type

    @property
    def result_type(self) -> FileResultType:
        return self._result_type

    @property
    def success(self) -> bool:
        return self._result_type == FileResultType.SUCCESS


class LoadJsonResult(BasicFileResult):
    def __init__(self, result_type: FileResultType, data: dict) -> None:
        super().__init__(result_type)
        self._data: dict = data

    @property
    def data(self) -> dict:
        return self._data


class SaveJsonResult(BasicFileResult):
    def __init__(self, result_type: FileResultType) -> None:
        super().__init__(result_type)


class LoadFileResult(BasicFileResult):
    def __init__(self, result_type: FileResultType, data: str) -> None:
        super().__init__(result_type)
        self._data: str = data

    @property
    def data(self) -> str:
        return self._data

    def to_json_result(self, data: dict) -> LoadJsonResult:
        return LoadJsonResult(self.result_type, data)


class SaveFileResult(BasicFileResult):
    def __init__(self, result_type: FileResultType) -> None:
        super().__init__(result_type)

    def to_json_result(self) -> SaveJsonResult:
        return SaveJsonResult(self.result_type)


def load_file(path: Path) -> LoadFileResult:
    if not isinstance(path, Path):
        log(LogLevel.ERROR, f"path must be a Path object, not {type(path)}")
        return LoadFileResult(FileResultType.INVALID_PATH, "")

    if not path.exists():
        log(LogLevel.ERROR, f"File {path} does not exist")
        return LoadFileResult(FileResultType.FILE_NOT_FOUND, "")

    try:
        with open(path, 'r', encoding='utf-8') as f:
            data: str = f.read()
            return LoadFileResult(FileResultType.SUCCESS, data)

    except FileNotFoundError as e:
        log_exception(e, "while reading a file")
        return LoadFileResult(FileResultType.FILE_NOT_FOUND, "")
    except PermissionError as e:
        log_exception(e, "while reading a file")
        return LoadFileResult(FileResultType.PERMISSION_DENIED, "")
    except IsADirectoryError as e:
        log_exception(e, "while reading a file")
        return LoadFileResult(FileResultType.IS_A_DIRECTORY, "")
    except UnicodeDecodeError as e:
        log_exception(e, "while reading a file")
        return LoadFileResult(FileResultType.INVALID_ENCODING, "")
    except (IOError, OSError) as e:
        log_exception(e, "while reading a file")
        return LoadFileResult(FileResultType.IO_OR_OS_ERROR, "")

    except Exception as e:
        log_exception(e, "generic error while reading a file")
        return LoadFileResult(FileResultType.GENERIC, "")


def save_file(path: Path, data: str) -> SaveFileResult:
    if not isinstance(path, Path):
        log(LogLevel.ERROR, f"path must be a Path object, not {type(path)}")
        return SaveFileResult(FileResultType.INVALID_PATH)

    if not isinstance(data, str):
        log(LogLevel.ERROR, f"data must be a str to be able to store into a file, not {type(data)}")
        return SaveFileResult(FileResultType.INVALID_DATA)

    if path.exists() and path.is_dir():
        log(LogLevel.ERROR, f"File {path} is a directory")
        return SaveFileResult(FileResultType.IS_A_DIRECTORY)

    if not path.parent.exists():
        log(LogLevel.INFO, f"create directory {path.parent}")
        path.parent.mkdir(parents=True, exist_ok=True)

    if path.exists():
        log(LogLevel.INFO, f"overwrite file {path}")
    else:
        log(LogLevel.INFO, f"create file {path}")

    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(data)
            return SaveFileResult(FileResultType.SUCCESS)

    except FileNotFoundError as e:
        log_exception(e, "while reading a file")
        return SaveFileResult(FileResultType.FILE_NOT_FOUND)
    except PermissionError as e:
        log_exception(e, "while reading a file")
        return SaveFileResult(FileResultType.PERMISSION_DENIED)
    except IsADirectoryError as e:
        log_exception(e, "while reading a file")
        return SaveFileResult(FileResultType.IS_A_DIRECTORY)
    except UnicodeDecodeError as e:
        log_exception(e, "while reading a file")
        return SaveFileResult(FileResultType.INVALID_ENCODING)
    except (IOError, OSError) as e:
        log_exception(e, "while reading a file")
        return SaveFileResult(FileResultType.IO_OR_OS_ERROR)

    except Exception as e:
        log_exception(e, "unknown error while reading a file")
        return SaveFileResult(FileResultType.GENERIC)


def load_json(path: Path) -> LoadJsonResult:
    try:
        result: LoadFileResult = load_file(path)
        if not result.success:
            return result.to_json_result({})
        data: dict = json.loads(result.data)
        return result.to_json_result(data)

    except json.JSONDecodeError as e:
        log_exception(e, "while loading a JSON")
        return LoadJsonResult(FileResultType.INVALID_ENCODING, {})
    except RecursionError as e:
        log_exception(e, "while loading a JSON")
        return LoadJsonResult(FileResultType.RECURSION_ERROR, {})
    except OverflowError as e:
        log_exception(e, "while loading a JSON")
        return LoadJsonResult(FileResultType.OVERFLOW_ERROR, {})

    except Exception as e:
        log_exception(e, "unknown error while loading a JSON")
        return LoadJsonResult(FileResultType.GENERIC, {})

def save_json(path: Path, data: dict) -> SaveJsonResult:
    if not isinstance(data, dict):
        log(LogLevel.ERROR, f"data must be a dict to be able to serialise to JSON, not {type(data)}")
        return SaveJsonResult(FileResultType.INVALID_DATA)
    try:
        result: SaveFileResult =  save_file(path, json.dumps(data, indent=4))
        return result.to_json_result()

    except TypeError as e:
        log_exception(e, "while dumping a JSON")
        return SaveJsonResult(FileResultType.TYPE_ERROR)
    except ValueError as e:
        log_exception(e, "while dumping a JSON")
        return SaveJsonResult(FileResultType.VALUE_ERROR)
    except RecursionError as e:
        log_exception(e, "while dumping a JSON")
        return SaveJsonResult(FileResultType.RECURSION_ERROR)
    except OverflowError as e:
        log_exception(e, "while dumping a JSON")
        return SaveJsonResult(FileResultType.OVERFLOW_ERROR)

    except Exception as e:
        log_exception(e, "unknown error while dumping a JSON")
        return SaveJsonResult(FileResultType.GENERIC)
