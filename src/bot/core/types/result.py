from dataclasses import dataclass
from enum import Enum
from enum import auto
from typing import Optional
from typing import final


class ResultState(Enum):
    SUCCESS = auto()

    ERROR = auto()
    NO_DATA = auto()
    TYPE_MISSMATCH = auto()
    WHITESPACE_ERROR = auto()
    ALREADY_EXISTS = auto()
    EMPTY_NAME = auto()
    EMPTY_MESSAGE = auto()
    COUNTER_ERROR = auto()
    STILL_IN_USE = auto()
    BOT_DISABLED = auto()
    CHANNEL_DISABLED = auto()
    COMMAND_DISABLED = auto()
    ALIAS_DISABLED = auto()
    RESERVED_NAME = auto()
    UNABLE_TO_EXTRACT_ROLE = auto()
    MISSING_DATA = auto()
    USER_NOT_FOUND = auto()
    NO_QUOTES_FOUND = auto()
    INACTIVE_FEATURE = auto()
    PERMISSION_DENIED = auto()

    @property
    def success(self) -> bool:
        lucky_state = {ResultState.SUCCESS}
        return self in lucky_state

    @property
    def fail(self) -> bool:
        return not self.success


@dataclass
@final
class Result[T]:
    state: ResultState
    value: Optional[T] = None

    def cast_to[V](self, new_type: type[V], new_value: Optional[V] = None) -> "Result[V]":
        return Result(self.state, new_value)
