from collections.abc import Generator
from unittest.mock import patch

import pytest

from bot.core.alias_dict import alias_lookup
from bot.core.types.cooldown import CooldownsWrapper
from bot.core.types.programm_parts import PROGRAMM_PARTS
from bot.core.types.result import Result
from bot.core.types.result import ResultState
from bot.database.types.alias_dict_entry import AliasDictEntry


@pytest.fixture(autouse=True)
def setup_programm_parts() -> Generator[None, None, None]:
    with (
        patch("bot.core.app_context.APP_CONTEXT.twitch_live_message_cooldown_in_seconds.value", return_value=60),
        patch("bot.core.app_context.APP_CONTEXT.command_response_cooldown_in_seconds.value", return_value=60),
        patch("bot.core.app_context.APP_CONTEXT.alias_response_cooldown_in_seconds.value", return_value=60),
    ):
        PROGRAMM_PARTS.cooldowns = CooldownsWrapper()
        PROGRAMM_PARTS.cooldowns.alias_response_cooldown._data = {}  # type: ignore[reportPrivateUsage]
    yield


@pytest.mark.parametrize(
    ("message"),
    [
        "abf",
        "ABF",
        "abf\n123",
        "abf.",
        "abf,",
        "(abf)",
        "[abf]",
        "{abf}",
        '"abf"',
        "'abf'",
        "abf!",
        "abf?",
        "abf:",
        "abf;",
    ],
)
def test_alias_lookup_detects_alias_with_whitespace_and_punctuation(message: str) -> None:
    alias_result = Result(
        ResultState.SUCCESS,
        [AliasDictEntry(id=1, bot_id=1, alias="abf", explanation="test", enabled=True)],
    )

    with patch("bot.core.alias_dict.select_dict_from_bot_db", return_value=alias_result):
        lookup_result = alias_lookup(1, message, "broadcaster", 0, 0)

    assert lookup_result.state == ResultState.SUCCESS
    assert lookup_result.value == ["abf: test"]


@pytest.mark.parametrize(
    ("message"),
    [
        "abf123",
        "123abf",
        "xabfy",
        "abf-123",
        "fooabfbar",
    ],
)
def test_alias_lookup_does_not_detect_embedded_alias_tokens(message: str) -> None:
    alias_result = Result(
        ResultState.SUCCESS,
        [AliasDictEntry(id=1, bot_id=1, alias="abf", explanation="test", enabled=True)],
    )

    with patch("bot.core.alias_dict.select_dict_from_bot_db", return_value=alias_result):
        lookup_result = alias_lookup(1, message, "broadcaster", 0, 0)

    assert lookup_result.state == ResultState.SUCCESS
    assert lookup_result.value == []
