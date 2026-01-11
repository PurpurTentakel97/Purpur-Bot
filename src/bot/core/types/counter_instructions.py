from enum import Enum
from typing import Optional
from typing import final

from attr import dataclass


@final
class CounterOperation(Enum):
    ADD = "+"
    SUB = "-"


@final
@dataclass
class CounterInstructions:
    name: str
    operation: Optional[CounterOperation]
    value: Optional[int]
