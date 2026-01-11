from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import MetaData
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

# Core modules to test
import bot.core.bot as core_bot
import bot.core.commands as core_commands
import bot.core.counter as core_counter
import bot.core.discord as core_discord
import bot.core.discord_auth as core_discord_auth
import bot.core.startup as core_startup
import bot.core.terminate as core_terminate
import bot.core.twitch as core_twitch
import bot.core.twitch_auth as core_twitch_auth
from bot.core.types.counter_instructions import CounterOperation
from bot.core.types.programm_parts import PROGRAMM_PARTS
from bot.core.types.result import Result
from bot.core.types.result import ResultState
from bot.database.database import Database


@pytest.fixture
def engine() -> Engine:
    engine = create_engine("sqlite:///:memory:")
    metadata = MetaData()

    # Create tables needed for tests (matching database schema)
    Table(
        "bot_config",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("twitch_user_id", String),
        Column("name", String),
    )
    Table(
        "basic_commands",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("bot_id", Integer),
        Column("command", String),
        Column("message", String),
    )
    Table(
        "counter",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("bot_id", Integer),
        Column("name", String),
        Column("count", Integer, default=0),
    )
    Table(
        "bot_discord_lookup",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("bot_id", Integer),
        Column("server_id", Integer),
        Column("server_name", String),
    )
    Table(
        "discord_auth",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("discord_id", String, unique=True),
        Column("access_token", String),
        Column("refresh_token", String),
        Column("expires_at", Integer),
    )
    Table(
        "bot_twitch_lookup",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("bot_id", Integer),
        Column("channel_name", String),
    )
    Table(
        "twitch_auth",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("twitch_id", String, unique=True),
        Column("access_token", String),
        Column("refresh_token", String),
        Column("expires_at", Integer),
    )

    metadata.create_all(engine)
    return engine


@pytest.fixture(autouse=True)
def setup_db(engine: Engine) -> None:
    PROGRAMM_PARTS.database = Database(engine)
    PROGRAMM_PARTS.discord = None
    PROGRAMM_PARTS.twitch = None


# Tests for bot.py
@pytest.mark.asyncio
async def test_core_bot_operations() -> None:
    # Test add_bot
    res_add = core_bot.add_bot("  twitch_123  ")
    assert res_add.state == ResultState.SUCCESS
    bot_id = res_add.value
    assert bot_id is not None

    # Test update_bot (and get_bot)
    res_upd = core_bot.update_bot(bot_id, "  My New Bot  ")
    assert res_upd.state == ResultState.SUCCESS

    res_get = core_bot.get_bot(bot_id)
    assert res_get.state == ResultState.SUCCESS
    assert res_get.value is not None
    assert res_get.value.name == "My New Bot"

    # Test get_bots_by_twitch_id
    res_get_all = core_bot.get_bots_by_twitch_id(" twitch_123 ")
    assert res_get_all.state == ResultState.SUCCESS
    assert res_get_all.value is not None
    assert len(res_get_all.value) == 1

    # Test delete_bot
    with (
        patch("bot.core.bot.stop_all_twitch_bots_from_bot", new_callable=AsyncMock) as mock_stop_twitch,
        patch("bot.core.bot.stop_all_discord_bots_from_bot", new_callable=AsyncMock) as mock_stop_discord,
    ):
        res_del = await core_bot.delete_bot(bot_id)
        assert res_del.state == ResultState.SUCCESS
        mock_stop_twitch.assert_called_once_with(bot_id)
        mock_stop_discord.assert_called_once_with(bot_id)

    assert core_bot.get_bot(bot_id).state == ResultState.NO_DATA


# Tests for counter.py
def test_core_counter_operations() -> None:
    bot_id = 1
    # Test save_counter
    res_save = core_counter.save_counter(bot_id, " deaths ")
    assert res_save.state == ResultState.SUCCESS
    assert res_save.value is not None
    assert res_save.value.name == "deaths"

    # Test duplicate
    res_dup = core_counter.save_counter(bot_id, "DEATHS")
    assert res_dup.state == ResultState.ALREADY_EXISTS

    # Test increment/decrement
    res_inc = core_counter.increment_counter(bot_id, "deaths")
    assert res_inc.value is not None
    assert res_inc.value.count == 1

    res_inc_by = core_counter.increment_counter_by(bot_id, "deaths", 5)
    assert res_inc_by.value is not None
    assert res_inc_by.value.count == 6

    res_dec = core_counter.decrement_counter(bot_id, "deaths")
    assert res_dec.value is not None
    assert res_dec.value.count == 5

    res_dec_by = core_counter.decrement_counter_by(bot_id, "deaths", 2)
    assert res_dec_by.value is not None
    assert res_dec_by.value.count == 3

    # Test reset
    res_reset = core_counter.reset_counter(bot_id, "deaths")
    assert res_reset.value is not None
    assert res_reset.value.count == 0

    # Test edit name
    # We need to make sure _update_counter_names_in_commands doesn't fail
    # Since we have no commands, it should return True.
    res_edit = core_counter.edit_counter_name(bot_id, "deaths", "kills")
    assert res_edit.state == ResultState.SUCCESS
    assert res_edit.value is not None
    assert res_edit.value.name == "kills"
    assert core_counter.get_counter(bot_id, "deaths").state == ResultState.NO_DATA

    # Test get_counters_by_bot_id
    res_get_all = core_counter.get_counters_by_bot_id(bot_id)
    assert res_get_all.value is not None
    assert len(res_get_all.value) == 1

    # Test delete
    res_del = core_counter.delete_counter(bot_id, "kills")
    assert res_del.state == ResultState.SUCCESS
    assert core_counter.get_counter(bot_id, "kills").state == ResultState.NO_DATA


def test_core_counter_instructions() -> None:
    msg = "Score is {score} and deaths are {deaths+1} and level{level-2}"
    inst = core_counter.get_counter_instructions(msg)
    # Expected: score (None, None), deaths (ADD, 1), level (SUB, 2)
    # total 5 items.
    assert len(inst) == 5
    assert inst[0].name == "score"
    assert inst[1].name == "deaths"
    assert inst[1].operation == CounterOperation.ADD
    assert inst[1].value == 1
    assert inst[2].name == "deaths"
    assert inst[2].operation is None


def test_core_counter_in_use_delete() -> None:
    bot_id = 1
    core_counter.save_counter(bot_id, "points")
    # Mock select_commands_by_bot_id to return a command using "points"
    with patch("bot.core.counter.select_commands_by_bot_id_db") as mock_sel:
        mock_sel.return_value = Result(ResultState.SUCCESS, [MagicMock(message="Got {points}!")])
        res_del = core_counter.delete_counter(bot_id, "points")
        assert res_del.state == ResultState.SILL_IN_USE


# Tests for commands.py
def test_core_command_operations() -> None:
    bot_id = 1
    # Test save_command
    res_save = core_commands.save_command(bot_id, " !hello ", " World ")
    assert res_save.state == ResultState.SUCCESS
    assert res_save.value is not None
    assert res_save.value.command == "!hello"
    assert res_save.value.message == "World"

    # Test update message
    res_upd_msg = core_commands.update_command_message(bot_id, "!hello", "New World")
    assert res_upd_msg.value is not None
    assert res_upd_msg.value.message == "New World"

    # Test update name
    res_upd_name = core_commands.update_command_name(bot_id, "!hello", "!hi")
    assert res_upd_name.value is not None
    assert res_upd_name.value.command == "!hi"
    assert core_commands.get_command(bot_id, "!hello").state == ResultState.NO_DATA

    # Test get_commands_by_bot_id
    res_all = core_commands.get_commands_by_bot_id(bot_id)
    assert res_all.value is not None
    assert len(res_all.value) == 1

    # Test delete
    core_commands.delete_command(bot_id, "!hi")
    assert core_commands.get_command(bot_id, "!hi").state == ResultState.NO_DATA


def test_core_command_with_counter() -> None:
    bot_id = 1
    core_counter.save_counter(bot_id, "count")
    core_counter.increment_counter_by(bot_id, "count", 4)
    core_commands.save_command(bot_id, "!check", "Count is {count}")

    res = core_commands.get_command_with_counter(bot_id, "!check")
    assert res.value is not None
    assert res.value.message == "Count is 4"

    # Test with operation
    core_commands.save_command(bot_id, "!inc", "Inc to {count+1}")
    res_inc = core_commands.get_command_with_counter(bot_id, "!inc")
    assert res_inc.value is not None
    assert res_inc.value.message == "Inc to 5"
    counter_res = core_counter.get_counter(bot_id, "count")
    assert counter_res.value is not None
    assert counter_res.value.count == 5


def test_core_command_auto_create_counter() -> None:
    bot_id = 1
    # Saving a command with a new counter should create the counter
    core_commands.save_command(bot_id, "!new", "Value: {new_counter}")
    assert core_counter.get_counter(bot_id, "new_counter").state == ResultState.SUCCESS


# Tests for discord.py and discord_auth.py
def test_core_discord_auth() -> None:
    discord_id = 123
    res = core_discord_auth.store_or_update_discord_tokens(discord_id, "access", "refresh", 100)
    assert res.state == ResultState.SUCCESS

    res_get = core_discord_auth.get_discord_tokens(discord_id)
    assert res_get.value is not None
    assert res_get.value.access_token == "access"

    core_discord_auth.store_or_update_discord_tokens(discord_id, "new_access", "new_refresh", 200)
    res_get_after = core_discord_auth.get_discord_tokens(discord_id)
    assert res_get_after.value is not None
    assert res_get_after.value.access_token == "new_access"

    core_discord_auth.delete_discord_tokens(discord_id)
    assert core_discord_auth.get_discord_tokens(discord_id).state == ResultState.NO_DATA


@pytest.mark.asyncio
async def test_core_discord_operations() -> None:
    bot_id = 1
    discord_id = 456
    with patch("bot.core.discord.start_single_discord_bot", return_value=True) as mock_start:
        res = core_discord.add_discord_bot(bot_id, discord_id, " My Server ")
        assert res.state == ResultState.SUCCESS
        mock_start.assert_called_once_with(bot_id, discord_id)

    res_get = core_discord.get_discord_servers_by_bot_id(bot_id)
    assert res_get.value is not None
    assert len(res_get.value) == 1
    assert res_get.value[0].server_name == "My Server"

    with patch("bot.core.discord.stop_single_discord_bot", new_callable=AsyncMock, return_value=True) as mock_stop:
        res_del = await core_discord.delete_discord_bot(bot_id, discord_id)
        assert res_del.state == ResultState.SUCCESS
        mock_stop.assert_called_once_with(bot_id, discord_id)

    res_get_after = core_discord.get_discord_servers_by_bot_id(bot_id)
    assert res_get_after.value is not None
    assert len(res_get_after.value) == 0


# Tests for twitch.py and twitch_auth.py
def test_core_twitch_auth() -> None:
    twitch_id = "t123"
    core_twitch_auth.store_or_update_twitch_tokens(twitch_id, "a", "r", 10)
    res_get = core_twitch_auth.get_twitch_tokens(twitch_id)
    assert res_get.value is not None
    assert res_get.value.access_token == "a"

    core_twitch_auth.delete_twitch_tokens(twitch_id)
    assert core_twitch_auth.get_twitch_tokens(twitch_id).state == ResultState.NO_DATA


@pytest.mark.asyncio
async def test_core_twitch_operations() -> None:
    bot_id = 1
    channel = " MyChannel "
    with patch("bot.core.twitch.start_single_twitch_bot", new_callable=AsyncMock, return_value=True) as mock_start:
        res = await core_twitch.add_twitch_channel(bot_id, channel)
        assert res.state == ResultState.SUCCESS
        mock_start.assert_called_once_with(bot_id, "mychannel")

    res_get = core_twitch.get_twitch_channels_from_bot(bot_id)
    assert res_get.value is not None
    assert len(res_get.value) == 1
    assert res_get.value[0].channel_name == "mychannel"

    with patch("bot.core.twitch.stop_single_twitch_bot", new_callable=AsyncMock, return_value=True) as mock_stop:
        res_del = await core_twitch.delete_twitch_channel(bot_id, channel)
        assert res_del.state == ResultState.SUCCESS
        mock_stop.assert_called_once_with(bot_id, "mychannel")

    res_get_after = core_twitch.get_twitch_channels_from_bot(bot_id)
    assert res_get_after.value is not None
    assert len(res_get_after.value) == 0


# Tests for startup.py and terminate.py
@pytest.mark.asyncio
async def test_core_lifecycle() -> None:
    with (
        patch("bot.core.startup.Database.create") as mock_db_create,
        patch("bot.core.startup.DiscordClient.create", new_callable=AsyncMock) as mock_discord_create,
        patch("bot.core.startup.TwitchClient.create", new_callable=AsyncMock) as mock_twitch_create,
        patch("bot.core.startup.TwitchChat.create", new_callable=AsyncMock),
    ):
        mock_db = MagicMock()
        mock_db_create.return_value = mock_db

        mock_discord = MagicMock()
        mock_discord_create.return_value = mock_discord

        mock_twitch = MagicMock()
        mock_twitch_create.return_value = mock_twitch

        # Mock database selects for startup
        mock_db.select_all.side_effect = [
            Result(ResultState.SUCCESS, []),  # discord servers
            Result(ResultState.SUCCESS, []),  # twitch channels
        ]

        await core_startup.startup_programm()

        assert PROGRAMM_PARTS.database_unwrapped() == mock_db
        assert PROGRAMM_PARTS.discord == mock_discord
        assert PROGRAMM_PARTS.twitch == mock_twitch

        # Terminate
        mock_discord.terminate = AsyncMock()
        mock_twitch.terminate = AsyncMock()
        mock_db.close = MagicMock()

        await core_terminate.terminate_programm()

        mock_discord.terminate.assert_called_once()
        mock_twitch.terminate.assert_called_once()
        mock_db.close.assert_called_once()
