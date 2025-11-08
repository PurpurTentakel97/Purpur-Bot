from enum import Enum
from datetime import datetime

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
