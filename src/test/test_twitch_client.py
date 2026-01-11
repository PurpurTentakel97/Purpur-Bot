from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from twitchAPI.type import InvalidRefreshTokenException
from twitchAPI.type import TwitchAuthorizationException
from twitchAPI.type import UnauthorizedException

from bot.chat.twitch_client import TwitchClient
from bot.core.app_context import TwitchTokens
from bot.helpers.log import LogLevel


@pytest.mark.asyncio
async def test_twitch_client_create_success_with_tokens() -> None:
    # Mock tokens in APP_CONTEXT
    tokens = TwitchTokens("access", "refresh")

    with (
        patch("bot.chat.twitch_client.APP_CONTEXT") as mock_ctx,
        patch("bot.chat.twitch_client.Twitch", new_callable=AsyncMock) as mock_twitch_cls,
    ):
        mock_ctx.twitch_tokens.is_valid.return_value = True
        mock_ctx.twitch_tokens.value_or_rise.return_value = tokens
        mock_ctx.twitch_client_id.is_valid.return_value = True
        mock_ctx.twitch_client_id.value_or_rise.return_value = "id"
        mock_ctx.twitch_credentials.is_valid.return_value = True
        mock_ctx.twitch_credentials.value_or_rise.return_value = "cred"

        mock_twitch_instance = mock_twitch_cls.return_value

        client = await TwitchClient.create()

        assert isinstance(client, TwitchClient)
        assert client.client == mock_twitch_instance

        mock_twitch_cls.assert_called_once_with("id", "cred", authenticate_app=False)
        mock_twitch_instance.set_user_authentication.assert_called_once_with(
            "access",
            TwitchClient._SCOPES,  # type: ignore[reportPrivateUsage]
            "refresh",
            validate=True,
        )


@pytest.mark.asyncio
async def test_twitch_client_create_no_tokens() -> None:
    with (
        patch("bot.chat.twitch_client.APP_CONTEXT") as mock_ctx,
        patch("bot.chat.twitch_client.Twitch", new_callable=AsyncMock) as mock_twitch_cls,
        patch("bot.chat.twitch_client.UserAuthenticator", new_callable=MagicMock) as mock_auth_cls,
    ):
        mock_ctx.twitch_tokens.is_valid.return_value = False
        mock_ctx.twitch_client_id.is_valid.return_value = True
        mock_ctx.twitch_client_id.value_or_rise.return_value = "id"
        mock_ctx.twitch_credentials.is_valid.return_value = True
        mock_ctx.twitch_credentials.value_or_rise.return_value = "cred"

        mock_twitch_instance = mock_twitch_cls.return_value

        mock_auth_instance = mock_auth_cls.return_value
        mock_auth_instance.authenticate = AsyncMock(return_value=("new_access", "new_refresh"))

        client = await TwitchClient.create()

        assert isinstance(client, TwitchClient)
        mock_twitch_cls.assert_called_once_with("id", "cred")
        mock_auth_cls.assert_called_once_with(mock_twitch_instance, TwitchClient._SCOPES)  # type: ignore[reportPrivateUsage]
        mock_ctx.update_twitch_tokens.assert_called_once_with("new_access", "new_refresh")
        mock_twitch_instance.set_user_authentication.assert_called_once_with(
            "new_access",
            TwitchClient._SCOPES,  # type: ignore[reportPrivateUsage]
            "new_refresh",
            validate=True,
        )


@pytest.mark.asyncio
async def test_twitch_client_create_invalid_tokens_reauth() -> None:
    tokens = TwitchTokens("old_access", "old_refresh")

    with (
        patch("bot.chat.twitch_client.APP_CONTEXT") as mock_ctx,
        patch("bot.chat.twitch_client.Twitch", new_callable=AsyncMock) as mock_twitch_cls,
        patch("bot.chat.twitch_client.UserAuthenticator", new_callable=MagicMock) as mock_auth_cls,
    ):
        mock_ctx.twitch_tokens.is_valid.return_value = True
        mock_ctx.twitch_tokens.value_or_rise.return_value = tokens
        mock_ctx.twitch_client_id.is_valid.return_value = True
        mock_ctx.twitch_client_id.value_or_rise.return_value = "id"
        mock_ctx.twitch_credentials.is_valid.return_value = True
        mock_ctx.twitch_credentials.value_or_rise.return_value = "cred"

        mock_twitch_instance = mock_twitch_cls.return_value
        # The first call fails with UnauthorizedException, the second succeeds
        mock_twitch_instance.set_user_authentication.side_effect = [UnauthorizedException(), None]

        mock_auth_instance = mock_auth_cls.return_value
        mock_auth_instance.authenticate = AsyncMock(return_value=("new_access", "new_refresh"))

        client = await TwitchClient.create()

        assert isinstance(client, TwitchClient)
        assert mock_twitch_instance.set_user_authentication.call_count == 2
        mock_ctx.update_twitch_tokens.assert_called_once_with("new_access", "new_refresh")

        # Verify the second call used new tokens
        mock_twitch_instance.set_user_authentication.assert_called_with(
            "new_access",
            TwitchClient._SCOPES,  # type: ignore[reportPrivateUsage]
            "new_refresh",
            validate=True,
        )


@pytest.mark.asyncio
async def test_twitch_client_create_auth_failure_all_attempts() -> None:
    tokens = TwitchTokens("old_access", "old_refresh")

    with (
        patch("bot.chat.twitch_client.APP_CONTEXT") as mock_ctx,
        patch("bot.chat.twitch_client.Twitch", new_callable=AsyncMock) as mock_twitch_cls,
        patch("bot.chat.twitch_client.UserAuthenticator", new_callable=MagicMock) as mock_auth_cls,
        patch("bot.chat.twitch_client.log_twitch") as mock_log,
    ):
        mock_ctx.twitch_tokens.is_valid.return_value = True
        mock_ctx.twitch_tokens.value_or_rise.return_value = tokens
        mock_ctx.twitch_client_id.is_valid.return_value = True
        mock_ctx.twitch_client_id.value_or_rise.return_value = "id"
        mock_ctx.twitch_credentials.is_valid.return_value = True
        mock_ctx.twitch_credentials.value_or_rise.return_value = "cred"

        mock_twitch_instance = mock_twitch_cls.return_value
        # All attempts fail
        mock_twitch_instance.set_user_authentication.side_effect = UnauthorizedException()

        mock_auth_instance = mock_auth_cls.return_value
        mock_auth_instance.authenticate = AsyncMock(return_value=("new_access", "new_refresh"))

        client = await TwitchClient.create()

        assert client is None
        assert mock_twitch_instance.set_user_authentication.call_count == 2
        mock_log.assert_called_with(LogLevel.ERROR, "Twitch authentication failed: ")
    tokens = TwitchTokens("old_access", "old_refresh")
    with (
        patch("bot.chat.twitch_client.APP_CONTEXT") as mock_ctx,
        patch("bot.chat.twitch_client.Twitch", new_callable=AsyncMock) as mock_twitch_cls,
        patch("bot.chat.twitch_client.log_twitch") as mock_log,
    ):
        mock_ctx.twitch_tokens.is_valid.return_value = False
        mock_ctx.twitch_client_id.is_valid.return_value = True
        mock_ctx.twitch_client_id.value_or_rise.return_value = "id"
        mock_ctx.twitch_credentials.is_valid.return_value = True
        mock_ctx.twitch_credentials.value_or_rise.return_value = "cred"
        mock_twitch_cls.side_effect = TwitchAuthorizationException("Auth failed")
        client = await TwitchClient.create()
        assert client is None
        mock_log.assert_called_with(LogLevel.ERROR, "Twitch connection failed: Auth failed")
    tokens = TwitchTokens("old_access", "old_refresh")

    with (
        patch("bot.chat.twitch_client.APP_CONTEXT") as mock_ctx,
        patch("bot.chat.twitch_client.Twitch", new_callable=AsyncMock) as mock_twitch_cls,
        patch("bot.chat.twitch_client.UserAuthenticator", new_callable=MagicMock) as mock_auth_cls,
    ):
        mock_ctx.twitch_tokens.is_valid.return_value = True
        mock_ctx.twitch_tokens.value_or_rise.return_value = tokens
        mock_ctx.twitch_client_id.is_valid.return_value = True
        mock_ctx.twitch_client_id.value_or_rise.return_value = "id"
        mock_ctx.twitch_credentials.is_valid.return_value = True
        mock_ctx.twitch_credentials.value_or_rise.return_value = "cred"

        mock_twitch_instance = mock_twitch_cls.return_value
        # The first call fails with InvalidRefreshTokenException, the second succeeds
        mock_twitch_instance.set_user_authentication.side_effect = [InvalidRefreshTokenException(), None]

        mock_auth_instance = mock_auth_cls.return_value
        mock_auth_instance.authenticate = AsyncMock(return_value=("new_access", "new_refresh"))

        client = await TwitchClient.create()

        assert isinstance(client, TwitchClient)
        assert mock_twitch_instance.set_user_authentication.call_count == 2
        mock_ctx.update_twitch_tokens.assert_called_once_with("new_access", "new_refresh")

        # Verify the second call used new tokens
        mock_twitch_instance.set_user_authentication.assert_called_with(
            "new_access",
            TwitchClient._SCOPES,  # type: ignore[reportPrivateUsage]
            "new_refresh",
            validate=True,
        )
