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


def _log_call_default(config_level: LogLevel, call_level: LogLevel, message: str) -> None:
    LogLevelConfig.default.level = config_level
    log_default(call_level, message)


def _log_call_discord(config_level: LogLevel, call_level: LogLevel, message: str) -> None:
    LogLevelConfig.discord.level = config_level
    log_discord(call_level, message)


def _log_call_twitch(config_level: LogLevel, call_level: LogLevel, message: str) -> None:
    LogLevelConfig.twitch.level = config_level
    log_twitch(call_level, message)


@pytest.mark.parametrize(
    "config_level", [LogLevel.DEBUG, LogLevel.INFO, LogLevel.WARNING, LogLevel.ERROR, LogLevel.CRITICAL]
)
@pytest.mark.parametrize(
    "call_level", [LogLevel.DEBUG, LogLevel.INFO, LogLevel.WARNING, LogLevel.ERROR, LogLevel.CRITICAL]
)
@pytest.mark.parametrize("log_function", [_log_call_default, _log_call_discord, _log_call_twitch])
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


@pytest.mark.parametrize(
    "log_level, expected_string",
    [
        (LogLevel.DEBUG, "DEBUG"),
        (LogLevel.INFO, "INFO"),
        (LogLevel.WARNING, "WARNING"),
        (LogLevel.ERROR, "ERROR"),
        (LogLevel.CRITICAL, "CRITICAL"),
    ],
)
def test_correct_log_level(capsys: pytest.CaptureFixture[str], log_level: LogLevel, expected_string: str) -> None:
    _reset_log()

    log_default(log_level, "test message")
    captured: CaptureResult[str] = capsys.readouterr()
    assert expected_string in captured.out


@pytest.mark.parametrize(
    "log_function, expected_string", [(log_default, "Default"), (log_discord, "Discord"), (log_twitch, "Twitch")]
)
def test_correct_log_program(
    capsys: pytest.CaptureFixture[str], log_function: Callable[[LogLevel, str], None], expected_string: str
) -> None:
    _reset_log()

    log_function(LogLevel.DEBUG, "test message")
    captured: CaptureResult[str] = capsys.readouterr()
    assert expected_string in captured.out
