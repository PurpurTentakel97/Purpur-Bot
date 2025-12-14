from dataclasses import dataclass
from enum import Enum, auto, IntEnum
from datetime import datetime
from functools import lru_cache
from types import TracebackType
from typing import ClassVar


class LogProgram(Enum):
    Default = auto()
    Discord = auto()
    Twitch = auto()

    def __str__(self) -> str:
        return self.name

    @classmethod
    @lru_cache(maxsize=1)
    def max_length(cls) -> int:
        return max(len(member.name) for member in cls)


class LogLevel(IntEnum):
    DEBUG = 10
    INFO = 20
    ERROR = 30
    CRITICAL = 40

    DEFAULT_LOG_LEVEL: ClassVar["LogLevel"] = DEBUG

    def __str__(self) -> str:
        return self.name

    @classmethod
    @lru_cache(maxsize=1)
    def max_length(cls) -> int:
        return max(len(member.name) for member in cls)


@dataclass
class LogLevelConfigEntry:
    _level: LogLevel = LogLevel.DEFAULT_LOG_LEVEL

    @property
    def level(self) -> LogLevel:
        return self._level

    @level.setter
    def level(self, level: LogLevel) -> None:
        self._level = level

    def should_log(self, provided: LogLevel) -> bool:
        return self._level <= provided


class LogLevelConfig:
    def __new__(cls, *args, **kwargs) -> None:
        raise TypeError("LogLevelConfig is a static namespace class. Access it via the LogLevelConfig class")

    default: ClassVar[LogLevelConfigEntry] = LogLevelConfigEntry()
    discord: ClassVar[LogLevelConfigEntry] = LogLevelConfigEntry()
    twitch: ClassVar[LogLevelConfigEntry] = LogLevelConfigEntry()

    @classmethod
    def reset(cls) -> None:
        cls.default.level = LogLevel.DEFAULT_LOG_LEVEL
        cls.discord.level = LogLevel.DEFAULT_LOG_LEVEL
        cls.twitch.level = LogLevel.DEFAULT_LOG_LEVEL


def log(level: LogLevel, program: LogProgram, message: str) -> None:
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] |"
          f" {level!s:{LogLevel.max_length()}} |"
          f" {program!s:{LogProgram.max_length()}} |"
          f" {message}")


def log_default(level: LogLevel, message: str) -> None:
    if LogLevelConfig.default.should_log(level):
        log(level=level,
            program=LogProgram.Default,
            message=message)


def log_discord(level: LogLevel, message: str) -> None:
    if LogLevelConfig.discord.should_log(level):
        log(level=level,
            program=LogProgram.Discord,
            message=message)


def log_twitch(level: LogLevel, message: str) -> None:
    if LogLevelConfig.twitch.should_log(level):
        log(level=level,
            program=LogProgram.Twitch,
            message=message)


def log_exception(exception: Exception, program: LogProgram, message: str) -> None:
    exception_name: str = type(exception).__name__
    trace_back: TracebackType | None = exception.__traceback__
    location: str = "unknown location"

    if trace_back is not None:
        filename: str = trace_back.tb_frame.f_code.co_filename
        line_number: int = trace_back.tb_lineno
        function_name: str = trace_back.tb_frame.f_code.co_name

        location = f"{filename}:{line_number} in {function_name}()"

    log(level=LogLevel.CRITICAL,
        program=program,
        message=f"{exception_name} | {location} | {message}")
