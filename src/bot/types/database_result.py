from enum import Enum
from enum import auto
from typing import Self


class DatabaseResult(Enum):
    SUCCESS = auto()
    ERROR = auto()
    EMPTY = auto()
    TYPE_MISSMATCH = auto()
    NO_DATA_EDITED = auto()

    @classmethod
    def is_success(cls, result: Self) -> bool:
        return result == cls.SUCCESS
