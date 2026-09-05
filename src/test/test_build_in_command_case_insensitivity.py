"""Tests for the case-insensitive routing of ``handle_build_in_command``.

The command matcher dispatches on a lower-cased copy of the message tokens
(``route``) while every argument that ends up in business logic or in a
response is read back from the original ``tokens``. These tests lock in both
halves of that contract:

* keyword / subcommand casing does not matter for routing, and
* identifiers and free-text payloads keep the casing the user typed.

``test_all_match_keywords_are_lowercase`` additionally keeps the ``match``
statement in sync with the "route is lower-cased" contract.
"""

import ast
import inspect
from pathlib import Path
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

import bot.chat.handle_commands as handle_commands_module
from bot.chat.handle_commands import handle_build_in_command
from bot.core.types.permission_level import PermissionLevel
from bot.core.types.result import Result
from bot.core.types.result import ResultState
from bot.database.types.alias_dict_entry import AliasDictEntry
from bot.database.types.base_command import BasicCommandDB
from bot.database.types.counter import CounterDB
from bot.database.types.feature_flags import FeatureFlagsDB


@pytest.fixture
def feature_flags() -> FeatureFlagsDB:
    return FeatureFlagsDB(
        id=1,
        bot_id=1,
        can_commands=True,
        can_alias=True,
        can_broadcast=True,
        can_twitch_live=True,
        can_quote=True,
    )


def _message(text: str) -> MagicMock:
    message = MagicMock()
    message.text = text
    message.bot_id = 1
    message.sender_permission_level = PermissionLevel.ADMIN
    message.has_twitch_message = True
    message.has_discord_message = False
    message.try_get_twitch_broadcaster_id = MagicMock(return_value="12345")
    message.try_get_discord_server_id = MagicMock(return_value=0)
    message.try_get_discord_channel_id = MagicMock(return_value=0)
    message.to_response_message = lambda text: text  # type: ignore[reportUnknownLambdaType, assignment]
    return message


@pytest.mark.parametrize("command_word", ["!com", "!COM", "!Com", "!cOm"])
@pytest.mark.parametrize("sub_word", ["add", "ADD", "Add"])
@pytest.mark.asyncio
async def test_com_add_routes_case_insensitively_and_keeps_payload_casing(
    command_word: str, sub_word: str, feature_flags: FeatureFlagsDB
) -> None:
    message = _message(f"{command_word} {sub_word} MyCmd Hallo Welt")
    saved = Result(
        ResultState.SUCCESS,
        BasicCommandDB(
            id=1,
            bot_id=1,
            command="mycmd",
            message="Hallo Welt",
            enabled=True,
            permission_level=PermissionLevel.USER,
        ),
    )

    with patch("bot.chat.handle_commands.save_command_core", return_value=saved) as mock_save:
        await handle_build_in_command(message, feature_flags)

    mock_save.assert_called_once_with(1, "MyCmd", "Hallo Welt")


@pytest.mark.parametrize("text", ["!counter increment_by", "!COUNTER INCREMENT_BY", "!Counter Increment_By"])
@pytest.mark.asyncio
async def test_counter_increment_by_routes_case_insensitively_and_keeps_name_casing(
    text: str, feature_flags: FeatureFlagsDB
) -> None:
    message = _message(f"{text} MyCtr 5")
    updated = Result(ResultState.SUCCESS, CounterDB(id=1, bot_id=1, name="myctr", count=5))

    with patch("bot.chat.handle_commands.increment_counter_by_core", return_value=updated) as mock_increment:
        await handle_build_in_command(message, feature_flags)

    mock_increment.assert_called_once_with(1, "MyCtr", 5)


@pytest.mark.parametrize("text", ["!alias add", "!ALIAS ADD", "!Alias Add"])
@pytest.mark.asyncio
async def test_alias_add_routes_case_insensitively_and_keeps_explanation_casing(
    text: str, feature_flags: FeatureFlagsDB
) -> None:
    message = _message(f"{text} myAlias Some MixedCase Text")
    saved = Result(
        ResultState.SUCCESS,
        AliasDictEntry(id=1, bot_id=1, alias="myalias", explanation="Some MixedCase Text", enabled=True),
    )

    with patch("bot.chat.handle_commands.add_alias_core", return_value=saved) as mock_add:
        await handle_build_in_command(message, feature_flags)

    mock_add.assert_called_once_with(1, "myAlias", "Some MixedCase Text")


@pytest.mark.parametrize("text", ["!quote add", "!QUOTE ADD", "!Quote Add"])
@pytest.mark.asyncio
async def test_quote_add_routes_case_insensitively_and_keeps_payload_casing(
    text: str, feature_flags: FeatureFlagsDB
) -> None:
    message = _message(f"{text} @LimQuats says Hi There")
    save_mock = AsyncMock(return_value=Result(ResultState.SUCCESS, 1))

    with patch("bot.chat.handle_commands.save_quote_by_message", new=save_mock):
        await handle_build_in_command(message, feature_flags)

    save_mock.assert_awaited_once_with("@LimQuats says Hi There", message)


@pytest.mark.parametrize("command_word", ["!quote", "!QUOTE", "!Quote"])
@pytest.mark.asyncio
async def test_quote_lookup_routes_case_insensitively_and_keeps_name_casing(
    command_word: str, feature_flags: FeatureFlagsDB
) -> None:
    message = _message(f"{command_word} @LimQuats")
    get_mock = AsyncMock(return_value=Result(ResultState.SUCCESS, "a quote"))

    with patch("bot.chat.handle_commands.get_quote", new=get_mock):
        await handle_build_in_command(message, feature_flags)

    get_mock.assert_awaited_once_with("@LimQuats", message)


@pytest.mark.parametrize("command_word", ["!title", "!TITLE", "!Title"])
@pytest.mark.asyncio
async def test_title_routes_case_insensitively_and_keeps_payload_casing(
    command_word: str, feature_flags: FeatureFlagsDB
) -> None:
    message = _message(f"{command_word} My Stream Title")
    twitch = MagicMock()
    twitch.send_change_title = AsyncMock(return_value="ok")

    with patch("bot.chat.handle_commands.PROGRAMM_PARTS") as programm_parts:
        programm_parts.twitch = twitch
        await handle_build_in_command(message, feature_flags)

    twitch.send_change_title.assert_awaited_once_with(message, "12345", "My Stream Title")


@pytest.mark.parametrize("command_word", ["!tags", "!TAGS", "!Tags"])
@pytest.mark.asyncio
async def test_tags_routes_case_insensitively_and_keeps_payload_casing(
    command_word: str, feature_flags: FeatureFlagsDB
) -> None:
    message = _message(f"{command_word} FirstTag SecondTag")
    twitch = MagicMock()
    twitch.send_change_tags = AsyncMock(return_value="ok")

    with patch("bot.chat.handle_commands.PROGRAMM_PARTS") as programm_parts:
        programm_parts.twitch = twitch
        await handle_build_in_command(message, feature_flags)

    twitch.send_change_tags.assert_awaited_once_with(message, "12345", ["FirstTag", "SecondTag"])


def test_all_match_keywords_are_lowercase() -> None:
    """Every string literal matched in ``handle_build_in_command`` must be lower-case.

    Routing happens on a lower-cased copy of the tokens, so an upper-case
    literal in a ``case`` pattern could never be reached.
    """
    source = Path(inspect.getfile(handle_commands_module)).read_text()
    tree = ast.parse(source)

    function: ast.AsyncFunctionDef | None = None
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "handle_build_in_command":
            function = node
            break
    assert function is not None, "handle_build_in_command not found"

    literals: list[str] = []
    for node in ast.walk(function):
        if isinstance(node, ast.MatchValue) and isinstance(node.value, ast.Constant):
            value = node.value.value
            if isinstance(value, str):
                literals.append(value)

    assert literals, "no match keywords found - test would be vacuous"
    non_lowercase = sorted({literal for literal in literals if literal != literal.lower()})
    assert non_lowercase == [], f"these match keywords can never be routed: {non_lowercase}"
