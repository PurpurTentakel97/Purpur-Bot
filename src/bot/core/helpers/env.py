import os

from bot.helpers.log import LogLevel
from bot.helpers.log import log_default


def get_env_var_or_default[T](key: str, default: T) -> T | str:
    value = os.getenv(key)
    if value is None or not value.strip():
        log_default(LogLevel.INFO, f"Environment variable '{key}' is not set, using default '{default}'")
        return default

    return value.strip()


def get_env_var_or_rise(key: str) -> str:
    value = os.getenv(key)
    if value is None or not value.strip():
        raise RuntimeError(f"Environment variable '{key}' is not set")
    return value.strip()


def get_env_var_as_int_or_default[T](key: str, default: T) -> T | int:
    value = os.getenv(key)
    if value is None or not value.strip():
        log_default(LogLevel.INFO, f"Environment variable '{key}' is not set, using default '{default}'")
        return default

    return int(value.strip())
