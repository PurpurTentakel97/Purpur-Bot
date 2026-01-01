from enum import Enum
from enum import auto


class DatabaseResult(Enum):
    SUCCESS = auto()
    ERROR = auto()
    EMPTY = auto()
    TYPE_MISSMATCH = auto()


def is_success(result: DatabaseResult) -> bool:
    return result == DatabaseResult.SUCCESS
