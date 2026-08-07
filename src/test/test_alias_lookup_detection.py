from collections.abc import Generator
from unittest.mock import patch

import pytest

from bot.core.alias_dict import add_alias
from bot.core.alias_dict import alias_lookup
from bot.core.alias_dict import edit_dict_alias
from bot.core.types.cooldown import CooldownsWrapper
from bot.core.types.programm_parts import PROGRAMM_PARTS
from bot.core.types.result import Result
from bot.core.types.result import ResultState
from bot.database.types.alias_dict_entry import AliasDictEntry
from bot.database.types.fields import FIELD_ALIAS_NAME


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


@pytest.mark.parametrize(
    ("alias_input", "expected_alias"),
    [
        ("abf,", "abf"),
        ("abf.", "abf"),
        ("(abf)", "abf"),
        ('"abf"', "abf"),
        ("[abf]", "abf"),
        ("{abf}", "abf"),
    ],
)
def test_add_alias_normalizes_punctuation_wrapped_alias_before_persisting(
    alias_input: str, expected_alias: str
) -> None:
    db_result = Result(
        ResultState.SUCCESS,
        AliasDictEntry(id=1, bot_id=1, alias="abf", explanation="test", enabled=True),
    )

    with patch("bot.core.alias_dict.insert_dict_entry_db", return_value=db_result) as insert_mock:
        result = add_alias(1, alias_input, "test")

    assert result.state == ResultState.SUCCESS
    insert_mock.assert_called_once_with(1, expected_alias, "test")


@pytest.mark.parametrize(
    ("alias_input", "expected_alias"),
    [
        ("abf-abf", "abf-abf"),
        ("abf_123", "abf_123"),
        ("abf/123", "abf/123"),
        ("abf:123", "abf:123"),
        ("abc-123", "abc-123"),
    ],
)
def test_add_alias_persists_alias_that_is_not_split_by_detection(alias_input: str, expected_alias: str) -> None:
    db_result = Result(
        ResultState.SUCCESS,
        AliasDictEntry(id=1, bot_id=1, alias=expected_alias, explanation="test", enabled=True),
    )

    with patch("bot.core.alias_dict.insert_dict_entry_db", return_value=db_result) as insert_mock:
        result = add_alias(1, alias_input, "test")

    assert result.state == ResultState.SUCCESS
    insert_mock.assert_called_once_with(1, expected_alias, "test")


@pytest.mark.parametrize(
    ("alias_input"),
    [
        "abc\t123",
        "abc\n123",
        "abc 123",
    ],
)
def test_add_alias_rejects_invalid_whitespace_split_alias(alias_input: str) -> None:
    with patch("bot.core.alias_dict.insert_dict_entry_db") as insert_mock:
        result = add_alias(1, alias_input, "test")

    assert result.state == ResultState.WHITESPACE_ERROR
    insert_mock.assert_not_called()


@pytest.mark.parametrize(
    ("alias_input", "expected_alias"),
    [
        ("abf,", "abf"),
        ("abf.", "abf"),
        ("(abf)", "abf"),
        ('"abf"', "abf"),
        ("[abf]", "abf"),
        ("{abf}", "abf"),
    ],
)
def test_edit_dict_alias_normalizes_punctuation_wrapped_alias_before_persisting(
    alias_input: str,
    expected_alias: str,
) -> None:
    db_result = Result(
        ResultState.SUCCESS,
        AliasDictEntry(id=1, bot_id=1, alias="abf", explanation="test", enabled=True),
    )

    with patch("bot.core.alias_dict.update_dict_entry_db", return_value=db_result) as update_mock:
        result = edit_dict_alias(1, "old_alias", alias_input)

    assert result.state == ResultState.SUCCESS
    update_mock.assert_called_once_with(1, "old_alias", {FIELD_ALIAS_NAME: expected_alias})


@pytest.mark.parametrize(
    ("alias_input", "expected_alias"),
    [
        ("abf-abf", "abf-abf"),
        ("abf_123", "abf_123"),
        ("abf/123", "abf/123"),
        ("abf:123", "abf:123"),
        ("abc-123", "abc-123"),
    ],
)
def test_edit_dict_alias_persists_alias_that_is_not_split_by_detection(alias_input: str, expected_alias: str) -> None:
    db_result = Result(
        ResultState.SUCCESS,
        AliasDictEntry(id=1, bot_id=1, alias=expected_alias, explanation="test", enabled=True),
    )

    with patch("bot.core.alias_dict.update_dict_entry_db", return_value=db_result) as update_mock:
        result = edit_dict_alias(1, "old_alias", alias_input)

    assert result.state == ResultState.SUCCESS
    update_mock.assert_called_once_with(1, "old_alias", {FIELD_ALIAS_NAME: expected_alias})


@pytest.mark.parametrize(
    ("alias_input"),
    [
        "abc\t123",
        "abc\n123",
        "abc 123",
    ],
)
def test_edit_dict_alias_rejects_invalid_whitespace_split_alias(alias_input: str) -> None:
    with patch("bot.core.alias_dict.update_dict_entry_db") as update_mock:
        result = edit_dict_alias(1, "old_alias", alias_input)

    assert result.state == ResultState.WHITESPACE_ERROR
    update_mock.assert_not_called()
