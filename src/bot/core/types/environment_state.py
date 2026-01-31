from enum import Enum

from bot.helpers.log import LogProgram
from bot.helpers.log import log_exception


class Environment(Enum):
    PRODUCTION = "PRODUCTION"
    DEVELOPMENT = "DEVELOPMENT"

    @classmethod
    def from_string(cls, value: str) -> "Environment":
        try:
            return cls[value.upper()]
        except (KeyError, AttributeError) as e:
            log_exception(
                e, LogProgram.Default, f"Failed to parse Environment from string: {value}. Defaulting to PRODUCTION."
            )
            return cls.PRODUCTION

    def is_production(self) -> bool:
        return self == Environment.PRODUCTION

    def is_development(self) -> bool:
        return self == Environment.DEVELOPMENT
