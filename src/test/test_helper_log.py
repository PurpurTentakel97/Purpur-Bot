import re
from collections.abc import Callable

import pytest
from _pytest.capture import CaptureResult

from bot.helpers.log import LogLevel
from bot.helpers.log import LogLevelConfig
from bot.helpers.log import log_default
from bot.helpers.log import log_discord
from bot.helpers.log import log_twitch


def _reset_log() -> None:
    LogLevelConfig.reset()


def test_default_log_state() -> None:
    _reset_log()

    assert LogLevelConfig.default.level == LogLevel.DEFAULT_LOG_LEVEL
    assert LogLevelConfig.discord.level == LogLevel.DEFAULT_LOG_LEVEL
    assert LogLevelConfig.twitch.level == LogLevel.DEFAULT_LOG_LEVEL
    assert LogLevel.DEFAULT_LOG_LEVEL == LogLevel.DEBUG


def test_output_format(capsys: pytest.CaptureFixture[str]) -> None:
    _reset_log()

    message: str = "test message"
    log_default(LogLevel.INFO, message)

    captured: CaptureResult[str] = capsys.readouterr()
    regex: str = (
        r"^\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}\]\s\|\s"  # timestamp
        + r"[A-Z]+\s+\|\s"  # Level
        + r"[A-Z][a-z]+\s+\|\s"  # Program
        + re.escape(message)  # Message
    )

    assert re.search(regex, captured.out, re.MULTILINE) is not None


def _log_test_default(config_level: LogLevel, call_level: LogLevel, message: str) -> None:
    LogLevelConfig.default.level = config_level
    log_default(call_level, message)


def _log_test_discord(config_level: LogLevel, call_level: LogLevel, message: str) -> None:
    LogLevelConfig.discord.level = config_level
    log_discord(call_level, message)


def _log_test_twitch(config_level: LogLevel, call_level: LogLevel, message: str) -> None:
    LogLevelConfig.twitch.level = config_level
    log_twitch(call_level, message)


@pytest.mark.parametrize(
    "config_level", [LogLevel.DEBUG, LogLevel.INFO, LogLevel.WARNING, LogLevel.ERROR, LogLevel.CRITICAL]
)
@pytest.mark.parametrize(
    "call_level", [LogLevel.DEBUG, LogLevel.INFO, LogLevel.WARNING, LogLevel.ERROR, LogLevel.CRITICAL]
)
@pytest.mark.parametrize("log_function", [_log_test_default, _log_test_discord, _log_test_twitch])
def test_should_not_log_below_level(
    capsys: pytest.CaptureFixture[str],
    config_level: LogLevel,
    call_level: LogLevel,
    log_function: Callable[[LogLevel, LogLevel, str], None],
) -> None:
    _reset_log()

    test_message: str = f"Testing config {config_level.name} with call {call_level.name}"
    log_function(config_level, call_level, test_message)

    captured: CaptureResult[str] = capsys.readouterr()

    should_have_logged: bool = call_level >= config_level
    if should_have_logged:
        assert test_message in captured.out
    else:
        assert captured.out == ""
