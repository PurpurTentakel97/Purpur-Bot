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

    def is_success(self) -> bool:
        lucky_state = {ResultState.SUCCESS}
        return self in lucky_state


@dataclass
@final
class Result[T]:
    state: ResultState
    value: Optional[T] = None

    def has_value(self) -> bool:
        return self.value is not None
