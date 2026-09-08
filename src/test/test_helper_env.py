import pytest

from bot.core.helpers.env import get_env_var_as_log_level_or_default
from bot.helpers.log import LogLevel


def test_log_level_from_valid_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SOME_LOG_LEVEL", "info")
    assert get_env_var_as_log_level_or_default("SOME_LOG_LEVEL", LogLevel.WARNING) == LogLevel.INFO


def test_log_level_unset_returns_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SOME_LOG_LEVEL", raising=False)
    assert get_env_var_as_log_level_or_default("SOME_LOG_LEVEL", LogLevel.WARNING) == LogLevel.WARNING


def test_log_level_invalid_returns_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SOME_LOG_LEVEL", "not-a-level")
    assert get_env_var_as_log_level_or_default("SOME_LOG_LEVEL", LogLevel.ERROR) == LogLevel.ERROR
