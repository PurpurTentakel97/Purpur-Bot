from enum import Enum, auto
from datetime import datetime
from types import TracebackType


class LogProgramm(Enum):
    General = auto()
    Discord = auto()
    Twitch = auto()

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

class LogLevel(Enum):
    INFO = auto()
    DEBUG = auto()
    ERROR = auto()
    CRITICAL = auto()

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

def log(level: LogLevel, programm: LogProgramm, message: str) -> None:
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] | {level:8} | {programm:7} | {message}")

def log_general(level: LogLevel, message: str) -> None:
    log(level,LogProgramm.General, message)

def log_discord(level: LogLevel, message: str) -> None:
    log(level,LogProgramm.Discord, message)

def log_twitch(level: LogLevel, message: str) -> None:
    log(level,LogProgramm.Twitch, message)

def log_exception(exception: Exception, programm: LogProgramm, message: str) -> None:
    exception_name: str = type(exception).__name__
    trace_back: TracebackType | None = exception.__traceback__
    location: str = "unknown location"

    if trace_back is not None:
        filename: str = trace_back.tb_frame.f_code.co_filename
        line_number: int = trace_back.tb_lineno
        function_name: str = trace_back.tb_frame.f_code.co_name

        location = f"{filename}:{line_number} in {function_name}()"

    log(LogLevel.CRITICAL,
        programm,
        f"{exception_name} | {location} | {message}")
