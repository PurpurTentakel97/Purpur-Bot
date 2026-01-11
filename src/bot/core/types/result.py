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

    def is_success(self) -> bool:
        lucky_state = {ResultState.SUCCESS}
        return self in lucky_state


@dataclass
@final
class Result[T]:
    state: ResultState
    value: Optional[T] = None

    def cast_to[V](self, new_type: type[V], new_value: Optional[V] = None) -> "Result[V]":
        return Result(self.state, new_value)
