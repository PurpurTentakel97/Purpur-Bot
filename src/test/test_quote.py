from collections.abc import Generator
from datetime import UTC
from datetime import datetime
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from discord.message import Message as DiscordMessage
from twitchAPI.chat import ChatMessage as TwitchMessage

from bot.chat.types.message import ChatMessage
from bot.core.quote import get_quote
from bot.core.quote import save_discord_quote_by_message
from bot.core.quote import save_quote_by_message
from bot.core.quote import save_twitch_quote_by_message
from bot.core.types.result import Result
from bot.core.types.result import ResultState
from bot.database.types.feature_flags import FeatureFlagsDB
from bot.database.types.quote import Quote


@pytest.fixture
def mock_programm_parts() -> Generator[MagicMock, None, None]:
    with patch("bot.core.quote.PROGRAMM_PARTS") as mock_parts:
        mock_parts.database = MagicMock()
        mock_parts.twitch = MagicMock()
        mock_parts.twitch.client = MagicMock()
        yield mock_parts


@pytest.fixture
def mock_twitch_message() -> MagicMock:
    message = MagicMock(spec=TwitchMessage)
    message.user = MagicMock()
    message.user.id = "123"
    message.user.display_name = "Sender"
    return message


@pytest.fixture
def mock_discord_message() -> MagicMock:
    message = MagicMock(spec=DiscordMessage)
    message.author = MagicMock()
    message.author.id = 456
    message.author.name = "DiscordSender"
    return message


@pytest.fixture
def mock_feature_flags() -> Generator[tuple[MagicMock, MagicMock], None, None]:
    with (
        patch("bot.core.quote.select_twitch_feature_flags_by_channel_name") as mock_twitch_flags,
        patch("bot.core.quote.select_discord_feature_flags_by_server_id") as mock_discord_flags,
    ):
        # Default to enabled
        flags = FeatureFlagsDB(
            id=1,
            bot_id=1,
            can_commands=True,
            can_alias=True,
            can_broadcast=True,
            can_twitch_live=True,
            can_quote=True,
        )
        mock_twitch_flags.return_value = Result(ResultState.SUCCESS, flags)
        mock_discord_flags.return_value = Result(ResultState.SUCCESS, flags)

        yield (mock_twitch_flags, mock_discord_flags)


@pytest.fixture
def mock_twitch_chat() -> MagicMock:
    from bot.chat.twitch_chat import TwitchChat

    chat = MagicMock(spec=TwitchChat)
    chat.is_twitch = True
    chat.is_discord = False
    chat.channel_name = "test_channel"
    return chat


@pytest.fixture
def mock_discord_chat() -> MagicMock:
    chat = MagicMock()
    chat.is_twitch = False
    chat.is_discord = True
    return chat


@pytest.fixture
def chat_message_twitch(mock_twitch_message: MagicMock, mock_twitch_chat: MagicMock) -> ChatMessage:
    mock_twitch_message.room = MagicMock()
    mock_twitch_message.room.room_id = "123"
    return ChatMessage(
        bot_id=1,
        text="@target hello",
        sender_chat=mock_twitch_chat,
        sender_permission_level=MagicMock(),
        original_message=mock_twitch_message,
        meta_data=None,
    )


@pytest.fixture
def chat_message_discord(mock_discord_message: MagicMock, mock_discord_chat: MagicMock) -> ChatMessage:
    mock_discord_message.guild = MagicMock()
    mock_discord_message.guild.id = 789
    return ChatMessage(
        bot_id=1,
        text="<@123> hello",
        sender_chat=mock_discord_chat,
        sender_permission_level=MagicMock(),
        original_message=mock_discord_message,
        meta_data=None,
    )


@pytest.mark.asyncio
async def test_save_twitch_quote_success(
    mock_programm_parts: MagicMock, chat_message_twitch: ChatMessage, mock_feature_flags: tuple[MagicMock, MagicMock]
) -> None:
    chat_message_twitch.text = "@target hello world"

    # Mock Twitch API user lookup
    mock_user = MagicMock()
    mock_user.id = "target_id"
    mock_programm_parts.twitch.client.get_users.return_value = AsyncMock()

    with patch("bot.core.quote.first", new_callable=AsyncMock) as mock_first:
        mock_first.return_value = mock_user

        with patch("bot.core.quote.insert_quote_db") as mock_insert:
            mock_insert.return_value = Result(ResultState.SUCCESS, 1)

            result = await save_twitch_quote_by_message("@target hello world", chat_message_twitch)

            assert result.state == ResultState.SUCCESS
            assert result.value == 1
            mock_insert.assert_called_once_with(bot_id=1, discord_id=None, twitch_id="target_id", quote="hello world")


@pytest.mark.asyncio
async def test_save_twitch_quote_no_at(
    chat_message_twitch: ChatMessage, mock_feature_flags: tuple[MagicMock, MagicMock]
) -> None:
    result = await save_twitch_quote_by_message("no_at hello", chat_message_twitch)
    assert result.state == ResultState.MISSING_DATA


@pytest.mark.asyncio
async def test_save_twitch_quote_no_quote(
    chat_message_twitch: ChatMessage, mock_feature_flags: tuple[MagicMock, MagicMock]
) -> None:
    result = await save_twitch_quote_by_message("@target", chat_message_twitch)
    assert result.state == ResultState.MISSING_DATA


@pytest.mark.asyncio
async def test_save_twitch_quote_user_not_found(
    mock_programm_parts: MagicMock, chat_message_twitch: ChatMessage, mock_feature_flags: tuple[MagicMock, MagicMock]
) -> None:
    chat_message_twitch.text = "@unknown hello"

    mock_programm_parts.twitch.client.get_users.return_value = AsyncMock()
    with patch("bot.core.quote.first", new_callable=AsyncMock) as mock_first:
        mock_first.return_value = None

        result = await save_twitch_quote_by_message("@unknown hello", chat_message_twitch)
        assert result.state == ResultState.USER_NOT_FOUND


@pytest.mark.asyncio
async def test_save_discord_quote_success(
    chat_message_discord: ChatMessage, mock_feature_flags: tuple[MagicMock, MagicMock], mock_programm_parts: MagicMock
) -> None:
    chat_message_discord.text = "<@123> discord quote"
    mention = MagicMock()
    mention.id = 123
    with patch.object(chat_message_discord.original_message, "mentions", [mention]):
        with patch("bot.core.quote.insert_quote_db") as mock_insert:
            mock_insert.return_value = Result(ResultState.SUCCESS, 2)

            result = await save_discord_quote_by_message("<@123> discord quote", chat_message_discord)

            assert result.state == ResultState.SUCCESS
            assert result.value == 2
            mock_insert.assert_called_once_with(bot_id=1, discord_id=123, twitch_id=None, quote="discord quote")


@pytest.mark.asyncio
async def test_save_discord_quote_no_mention_prefix(
    chat_message_discord: ChatMessage, mock_feature_flags: tuple[MagicMock, MagicMock]
) -> None:
    result = await save_discord_quote_by_message("not a mention", chat_message_discord)
    assert result.state == ResultState.MISSING_DATA


@pytest.mark.asyncio
async def test_save_discord_quote_no_quote(
    chat_message_discord: ChatMessage, mock_feature_flags: tuple[MagicMock, MagicMock]
) -> None:
    result = await save_discord_quote_by_message("<@123>", chat_message_discord)
    assert result.state == ResultState.MISSING_DATA


@pytest.mark.asyncio
async def test_save_discord_quote_no_mentions_in_obj(
    chat_message_discord: ChatMessage, mock_feature_flags: tuple[MagicMock, MagicMock], mock_programm_parts: MagicMock
) -> None:
    chat_message_discord.text = "<@123> hello"
    with patch.object(chat_message_discord.original_message, "mentions", []):
        result = await save_discord_quote_by_message("<@123> hello", chat_message_discord)
        assert result.state == ResultState.USER_NOT_FOUND


@pytest.mark.asyncio
async def test_get_quote_random(
    chat_message_twitch: ChatMessage, mock_feature_flags: tuple[MagicMock, MagicMock]
) -> None:
    mock_quote = Quote(
        id=1, bot_id=1, discord_user_id=None, twitch_user_id="123", timestamp=datetime.now(UTC), quote="Random Quote"
    )

    with patch("bot.core.quote.select_quote_by_bot_id_db") as mock_select:
        mock_select.return_value = Result(ResultState.SUCCESS, [mock_quote])

        with patch("bot.core.quote.get_twitch_user_by_id", new_callable=AsyncMock) as mock_get_user:
            mock_user = MagicMock()
            mock_user.display_name = "TargetUser"
            mock_get_user.return_value = Result(ResultState.SUCCESS, mock_user)

            result = await get_quote("", chat_message_twitch)

            assert result.state == ResultState.SUCCESS
            assert result.value is not None
            assert "TargetUser" in result.value
            assert "Random Quote" in result.value


@pytest.mark.asyncio
async def test_get_quote_twitch_lookup_success(
    chat_message_twitch: ChatMessage, mock_feature_flags: tuple[MagicMock, MagicMock]
) -> None:
    mock_quote = Quote(
        id=1,
        bot_id=1,
        discord_user_id=None,
        twitch_user_id="target_id",
        timestamp=datetime.now(UTC),
        quote="Twitch Quote",
    )

    with patch("bot.core.quote.get_twitch_user_by_name", new_callable=AsyncMock) as mock_get_user_name:
        mock_user = MagicMock()
        mock_user.id = "target_id"
        mock_user.display_name = "TargetUser"
        mock_get_user_name.return_value = Result(ResultState.SUCCESS, mock_user)

        with patch("bot.core.quote.select_quote_by_twitch_id_db") as mock_select:
            mock_select.return_value = Result(ResultState.SUCCESS, [mock_quote])

            with patch("bot.core.quote.get_twitch_user_by_id", new_callable=AsyncMock) as mock_get_user_id:
                mock_get_user_id.return_value = Result(ResultState.SUCCESS, mock_user)

                result = await get_quote("@TargetUser", chat_message_twitch)

                assert result.state == ResultState.SUCCESS
                assert result.value is not None
                assert "Twitch Quote" in result.value


@pytest.mark.asyncio
async def test_get_quote_discord_lookup_mention(
    chat_message_discord: ChatMessage, mock_feature_flags: tuple[MagicMock, MagicMock], mock_programm_parts: MagicMock
) -> None:
    mock_quote = Quote(
        id=1, bot_id=1, discord_user_id=123, twitch_user_id=None, timestamp=datetime.now(UTC), quote="Discord Quote"
    )

    with patch("bot.core.quote.select_quote_by_discord_id_db") as mock_select:
        mock_select.return_value = Result(ResultState.SUCCESS, [mock_quote])

        with patch("bot.core.quote.get_discord_user_by_id", new_callable=AsyncMock) as mock_get_user:
            mock_user = MagicMock()
            mock_user.name = "DiscordUser"
            mock_get_user.return_value = Result(ResultState.SUCCESS, mock_user)

            result = await get_quote("<@123>", chat_message_discord)

            assert result.state == ResultState.SUCCESS
            assert result.value is not None
            assert "Discord Quote" in result.value
            assert "DiscordUser" in result.value


@pytest.mark.asyncio
async def test_get_quote_no_quotes_found(
    chat_message_twitch: ChatMessage, mock_feature_flags: tuple[MagicMock, MagicMock]
) -> None:
    with patch("bot.core.quote.get_twitch_user_by_name", new_callable=AsyncMock) as mock_get_user:
        mock_user = MagicMock()
        mock_user.id = "some_id"
        mock_get_user.return_value = Result(ResultState.SUCCESS, mock_user)

        with patch("bot.core.quote.select_quote_by_twitch_id_db") as mock_select:
            mock_select.return_value = Result(ResultState.SUCCESS, [])

            result = await get_quote("@UserWithNoQuotes", chat_message_twitch)
            assert result.state == ResultState.NO_QUOTES_FOUND


@pytest.mark.asyncio
async def test_save_quote_by_message_twitch(
    chat_message_twitch: ChatMessage, mock_feature_flags: tuple[MagicMock, MagicMock]
) -> None:
    with patch("bot.core.quote.save_twitch_quote_by_message", new_callable=AsyncMock) as mock_save:
        mock_save.return_value = Result(ResultState.SUCCESS, 1)
        result = await save_quote_by_message("hello", chat_message_twitch)
        assert result.state == ResultState.SUCCESS
        mock_save.assert_called_once_with("hello", chat_message_twitch)


@pytest.mark.asyncio
async def test_save_quote_by_message_discord(
    chat_message_discord: ChatMessage, mock_feature_flags: tuple[MagicMock, MagicMock]
) -> None:
    with patch("bot.core.quote.save_discord_quote_by_message", new_callable=AsyncMock) as mock_save:
        mock_save.return_value = Result(ResultState.SUCCESS, 2)
        result = await save_quote_by_message("hello", chat_message_discord)
        assert result.state == ResultState.SUCCESS
        mock_save.assert_called_once_with("hello", chat_message_discord)


@pytest.mark.asyncio
async def test_get_quote_no_data(
    chat_message_twitch: ChatMessage, mock_feature_flags: tuple[MagicMock, MagicMock]
) -> None:
    with patch("bot.core.quote.select_quote_by_bot_id_db") as mock_select:
        mock_select.return_value = Result(ResultState.NO_DATA, None)
        result = await get_quote("", chat_message_twitch)
        assert result.state == ResultState.NO_DATA


@pytest.mark.asyncio
async def test_quote_disabled_twitch(
    chat_message_twitch: ChatMessage, mock_feature_flags: tuple[MagicMock, MagicMock]
) -> None:
    mock_twitch_flags, _ = mock_feature_flags
    mock_twitch_flags.return_value = Result(
        ResultState.SUCCESS,
        FeatureFlagsDB(
            id=1,
            bot_id=1,
            can_commands=True,
            can_alias=True,
            can_broadcast=True,
            can_twitch_live=True,
            can_quote=False,
        ),
    )

    result = await save_quote_by_message("hello", chat_message_twitch)
    assert result.state == ResultState.INACTIVE_FEATURE


@pytest.mark.asyncio
async def test_quote_disabled_discord(
    chat_message_discord: ChatMessage, mock_feature_flags: tuple[MagicMock, MagicMock]
) -> None:
    _, mock_discord_flags = mock_feature_flags
    mock_discord_flags.return_value = Result(
        ResultState.SUCCESS,
        FeatureFlagsDB(
            id=1,
            bot_id=1,
            can_commands=True,
            can_alias=True,
            can_broadcast=True,
            can_twitch_live=True,
            can_quote=False,
        ),
    )

    result = await save_quote_by_message("hello", chat_message_discord)
    assert result.state == ResultState.INACTIVE_FEATURE
