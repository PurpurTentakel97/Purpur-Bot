from enum import Enum
from datetime import datetime
from types import TracebackType


class LogLevel(Enum):
    INFO = 0
    DEBUG = 1
    ERROR = 2
    CRITICAL = 3

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


def log(level: LogLevel, message: str) -> None:
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] | {level:8} | {message}")


def log_exception(exception: Exception, message: str) -> None:
    exception_name: str = type(exception).__name__
    trace_back: TracebackType | None = exception.__traceback__
    location: str = "unknown location"

    if trace_back is not None:
        filename: str = trace_back.tb_frame.f_code.co_filename
        line_number: int = trace_back.tb_lineno
        function_name: str = trace_back.tb_frame.f_code.co_name

        location = f"{filename}:{line_number} in {function_name}()"

    log(LogLevel.CRITICAL,
        f"{exception_name} | {location} | {message}")
