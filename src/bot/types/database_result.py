from enum import Enum
from enum import auto


class DatabaseResult(Enum):
    SUCCESS = auto()
    ERROR = auto()
    EMPTY = auto()
    TYPE_MISSMATCH = auto()
    NO_DATA_EDITED = auto()

    @property
    def success(self) -> bool:
        return self == DatabaseResult.SUCCESS
