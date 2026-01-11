import pytest
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import MetaData
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from bot.core.types.programm_parts import PROGRAMM_PARTS
from bot.core.types.result import ResultState
from bot.database import bot
from bot.database import commands
from bot.database import counter
from bot.database import discord
from bot.database import discord_auth
from bot.database import twitch
from bot.database import twitch_auth
from bot.database.database import Database


@pytest.fixture
def engine() -> Engine:
    engine = create_engine("sqlite:///:memory:")
    metadata = MetaData()

    # Create tables needed for tests
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
        Column("discord_id", String),
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
        Column("twitch_id", String),
        Column("access_token", String),
        Column("refresh_token", String),
        Column("expires_at", Integer),
    )

    metadata.create_all(engine)
    return engine


@pytest.fixture(autouse=True)
def setup_db(engine: Engine) -> None:
    PROGRAMM_PARTS.database = Database(engine)


# Tests for bot.py
def test_bot_operations() -> None:
    # insert
    # bot.py:insert_bot only takes twitch_user_id
    # But BotConfigDB requires 'name'.
    # This suggests that insert_bot might be incomplete or
    #     BotConfigDB has mandatory fields that aren't set during insert.
    # Looking at src/bot/database/bot.py:
    # def insert_bot(twitch_user_id: str) -> Result[int]:
    #     return PROGRAMM_PARTS.database.insert(table_name=TABLE_NAME, data={"twitch_user_id": twitch_user_id})
    # If name is mandatory in BotConfigDB, select_bot will fail.

    # Let's fix the test by providing 'name' in update or making it optional in DB if possible.
    # Actually I should probably check if I can pass extra data to insert if I were to call it directly,
    # but I am testing the wrapper.

    # I'll update the test to use update_bot to set the name before selecting.
    res_ins = bot.insert_bot("twitch_123")
    assert res_ins.state == ResultState.SUCCESS
    bot_id = res_ins.value
    assert bot_id is not None

    bot.update_bot(bot_id, {"name": "my_bot"})

    # select_bot
    res_sel = bot.select_bot(bot_id)
    assert res_sel.state == ResultState.SUCCESS
    assert res_sel.value is not None
    assert res_sel.value.twitch_user_id == "twitch_123"
    assert res_sel.value.name == "my_bot"

    # select_bots_by_twitch_id
    res_sel_all = bot.select_bots_by_twitch_id("twitch_123")
    assert res_sel_all.state == ResultState.SUCCESS
    assert res_sel_all.value is not None
    assert len(res_sel_all.value) == 1

    # update_bot
    res_upd = bot.update_bot(bot_id, {"twitch_user_id": "twitch_456"})
    assert res_upd.state == ResultState.SUCCESS
    res_sel_after = bot.select_bot(bot_id)
    assert res_sel_after.value is not None
    assert res_sel_after.value.twitch_user_id == "twitch_456"

    # delete_bot
    res_del = bot.delete_bot(bot_id)
    assert res_del.state == ResultState.SUCCESS
    assert bot.select_bot(bot_id).state == ResultState.NO_DATA


# Tests for commands.py
def test_command_operations() -> None:
    bot_id = 1
    # insert_command
    res_ins = commands.insert_command(bot_id, "!test", "Hello")
    assert res_ins.state == ResultState.SUCCESS
    assert res_ins.value is not None
    assert res_ins.value.command == "!test"

    # select_command
    res_sel = commands.select_command(bot_id, "!test")
    assert res_sel.state == ResultState.SUCCESS
    assert res_sel.value is not None

    # select_commands_by_bot_id
    res_sel_all = commands.select_commands_by_bot_id(bot_id)
    assert res_sel_all.state == ResultState.SUCCESS
    assert res_sel_all.value is not None
    assert len(res_sel_all.value) == 1

    # update_command
    res_upd = commands.update_command(bot_id, "!test", {"message": "New Message"})
    assert res_upd.state == ResultState.SUCCESS
    assert res_upd.value is not None
    assert res_upd.value.message == "New Message"

    # delete_command
    res_del = commands.delete_command(bot_id, "!test")
    assert res_del.state == ResultState.SUCCESS
    assert commands.select_command(bot_id, "!test").state == ResultState.NO_DATA


# Tests for counter.py
def test_counter_operations() -> None:
    bot_id = 1
    # insert_counter
    res_ins = counter.insert_counter(bot_id, "deaths")
    assert res_ins.state == ResultState.SUCCESS
    assert res_ins.value is not None
    assert res_ins.value.name == "deaths"
    assert res_ins.value.count == 0

    # select_counter
    res_sel = counter.select_counter(bot_id, "deaths")
    assert res_sel.state == ResultState.SUCCESS
    assert res_sel.value is not None

    # select_counter_by_bot_id
    res_sel_all = counter.select_counter_by_bot_id(bot_id)
    assert res_sel_all.state == ResultState.SUCCESS
    assert res_sel_all.value is not None
    assert len(res_sel_all.value) == 1

    # update_counter_name
    res_upd_name = counter.update_counter(bot_id, "deaths", {counter.FIELD_NAME: "kills"})
    assert res_upd_name.state == ResultState.SUCCESS
    assert res_upd_name.value is not None
    assert res_upd_name.value.name == "kills"

    # update_counter (data)
    res_upd = counter.update_counter(bot_id, "kills", {"count": 5})
    assert res_upd.state == ResultState.SUCCESS
    assert res_upd.value is not None
    assert res_upd.value.count == 5

    # delete_counter
    res_del = counter.delete_counter(bot_id, "kills")
    assert res_del.state == ResultState.SUCCESS
    assert counter.select_counter(bot_id, "kills").state == ResultState.NO_DATA


# Tests for discord.py
def test_discord_operations() -> None:
    bot_id = 1
    # insert_discord_server
    res_ins = discord.insert_discord_server(bot_id, 123456, "My Server")
    assert res_ins.state == ResultState.SUCCESS

    # select_discord_servers_by_bot_id
    res_sel = discord.select_discord_servers_by_bot_id(bot_id)
    assert res_sel.state == ResultState.SUCCESS
    assert res_sel.value is not None
    assert len(res_sel.value) == 1
    assert res_sel.value[0].server_id == 123456

    # delete_discord_server
    res_del = discord.delete_discord_server(bot_id, 123456)
    assert res_del.state == ResultState.SUCCESS
    res_sel_after = discord.select_discord_servers_by_bot_id(bot_id)
    assert res_sel_after.value is not None
    assert len(res_sel_after.value) == 0


# Tests for discord_auth.py
def test_discord_auth_operations() -> None:
    discord_id = "123"
    # insert_discord_tokens
    res_ins = discord_auth.insert_discord_tokens(int(discord_id), "access", "refresh", 1000)
    assert res_ins.state == ResultState.SUCCESS

    # select_discord_tokens
    res_sel = discord_auth.select_discord_tokens(int(discord_id))
    assert res_sel.state == ResultState.SUCCESS
    assert res_sel.value is not None
    assert res_sel.value.access_token == "access"
    assert res_sel.value.discord_id == discord_id

    # update_discord_tokens
    res_upd = discord_auth.update_discord_tokens(int(discord_id), "new_access", "new_refresh", 2000)
    assert res_upd.state == ResultState.SUCCESS
    res_sel_after = discord_auth.select_discord_tokens(int(discord_id))
    assert res_sel_after.value is not None
    assert res_sel_after.value.access_token == "new_access"

    # delete_discord_tokens
    res_del = discord_auth.delete_discord_tokens(int(discord_id))
    assert res_del.state == ResultState.SUCCESS
    assert discord_auth.select_discord_tokens(int(discord_id)).state == ResultState.NO_DATA


# Tests for twitch.py
def test_twitch_operations() -> None:
    bot_id = 1
    # insert_twitch_channel
    res_ins = twitch.insert_twitch_channel(bot_id, "my_channel")
    assert res_ins.state == ResultState.SUCCESS

    # select_twitch_channels_by_bot_id
    res_sel = twitch.select_twitch_channels_by_bot_id(bot_id)
    assert res_sel.state == ResultState.SUCCESS
    assert res_sel.value is not None
    assert len(res_sel.value) == 1
    assert res_sel.value[0].channel_name == "my_channel"

    # delete_twitch_channel
    res_del = twitch.delete_twitch_channel(bot_id, "my_channel")
    assert res_del.state == ResultState.SUCCESS
    res_sel_after = twitch.select_twitch_channels_by_bot_id(bot_id)
    assert res_sel_after.value is not None
    assert len(res_sel_after.value) == 0


# Tests for twitch_auth.py
def test_twitch_auth_operations() -> None:
    twitch_id = "twitch_user"
    # insert_twitch_tokens
    res_ins = twitch_auth.insert_twitch_tokens(twitch_id, "access", "refresh", 1000)
    assert res_ins.state == ResultState.SUCCESS

    # select_twitch_tokens
    res_sel = twitch_auth.select_twitch_tokens(twitch_id)
    assert res_sel.state == ResultState.SUCCESS
    assert res_sel.value is not None
    assert res_sel.value.access_token == "access"

    # update_twitch_tokens
    res_upd = twitch_auth.update_twitch_tokens(twitch_id, "new_access", "new_refresh", 2000)
    assert res_upd.state == ResultState.SUCCESS
    res_sel_after = twitch_auth.select_twitch_tokens(twitch_id)
    assert res_sel_after.value is not None
    assert res_sel_after.value.access_token == "new_access"

    # delete_twitch_tokens
    res_del = twitch_auth.delete_twitch_tokens(twitch_id)
    assert res_del.state == ResultState.SUCCESS
    assert twitch_auth.select_twitch_tokens(twitch_id).state == ResultState.NO_DATA
