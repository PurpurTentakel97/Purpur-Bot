from collections.abc import Callable
from http import HTTPStatus
from typing import Annotated
from typing import Final
from typing import Optional
from typing import Protocol

import jwt
from fastapi import Depends
from fastapi import HTTPException
from fastapi_decorators import Decorator
from fastapi_decorators import depends
from starlette.requests import Request

from bot.core.alias_dict import get_alias_by_id
from bot.core.bot import get_bot as get_bot_core
from bot.core.broadcast_messages import get_broadcast_message_by_id
from bot.core.commands import get_command_by_id
from bot.core.counter import get_counter_by_id
from bot.core.discord import get_discord_by_server_id
from bot.core.discord_feature_flags import select_discord_feature_flags_by_id
from bot.core.quote import get_quote_by_id
from bot.core.twitch import get_twitch_channel_by_name
from bot.core.twitch_broadcast_auth import get_broadcast_tokens
from bot.core.twitch_feature_flags import select_twitch_feature_flags_by_id
from bot.core.types.result import Result
from bot.database.types.alias_dict_entry import AliasDictEntry
from bot.database.types.base_command import BasicCommandDB
from bot.database.types.bot_config import BotConfigDB
from bot.database.types.counter import CounterDB
from bot.database.types.discord_server import DiscordServerDB
from bot.database.types.feature_flags import DiscordFeatureFlagsDB
from bot.database.types.feature_flags import TwitchFeatureFlagsDB
from bot.database.types.quote import Quote
from bot.database.types.twitch_broadcast_auth import TwitchBroadcastAuthDB
from bot.database.types.twitch_broadcast_message import TwitchBroadcastMessageDB
from bot.database.types.twitch_channel import TwitchChannelDB
from bot.frontend.helpers.route_utils import get_discord_session_cookie
from bot.frontend.helpers.route_utils import get_twitch_session_cookie
from bot.frontend.types.discord_user_info import DiscordUserInfo
from bot.frontend.types.twitch_user_info import TwitchUserInfo


def bot_owner_required() -> Decorator:
    @depends
    async def wrapper(
        bot_id: int,
        twitch_user: Annotated[TwitchUserInfo, Depends(get_owned_twitch_user)],
    ) -> None:
        get_owned_bot(bot_id, twitch_user)

    return wrapper


def twitch_owner_required() -> Decorator:
    @depends
    async def wrapper(
        twitch_user: Annotated[TwitchUserInfo, Depends(get_owned_twitch_user)],
    ) -> None:
        pass

    return wrapper


def get_owned_twitch_channel_broadcast_authentication(bot_id: int, channel_name: str) -> TwitchBroadcastAuthDB:
    res: Final = get_broadcast_tokens(bot_id, channel_name)
    if res.state.fail or not res.value:
        raise HTTPException(
            HTTPStatus.NOT_FOUND, f"Broadcast tokens aren't found for bot {bot_id} and channel {channel_name}"
        )
    return res.value


def get_owned_twitch_user(request: Request) -> TwitchUserInfo:
    user = get_optional_owned_twitch_user(request)
    if user is None:
        raise HTTPException(HTTPStatus.UNAUTHORIZED, "You are not logged in with Twitch")
    return user


def get_optional_owned_twitch_user(request: Request) -> Optional[TwitchUserInfo]:
    session_cookie = get_twitch_session_cookie(request)
    if session_cookie is None:
        return None

    try:
        return TwitchUserInfo(
            id_=session_cookie.user_id,
            login=session_cookie.login,
            display_name=session_cookie.display_name,
            profile_image_url=session_cookie.profile_image_url,
        )
    except (jwt.InvalidTokenError, KeyError):
        return None


def get_owned_discord_user(request: Request) -> DiscordUserInfo:
    user = get_optional_owned_discord_user(request)
    if user is None:
        raise HTTPException(HTTPStatus.UNAUTHORIZED, "You are not logged in with Discord")
    return user


def get_optional_owned_discord_user(request: Request) -> Optional[DiscordUserInfo]:
    session_cookie = get_discord_session_cookie(request)
    if session_cookie is None:
        return None

    try:
        return DiscordUserInfo(
            id_=session_cookie.user_id,
            username=session_cookie.username,
            display_name=session_cookie.display_name,
            avatar_url=session_cookie.avatar_url,
        )
    except (jwt.InvalidTokenError, KeyError):
        return None


def get_bot(bot_id: int) -> BotConfigDB:
    bot = get_bot_core(bot_id)
    if bot.state.fail or bot.value is None:
        raise HTTPException(HTTPStatus.NOT_FOUND, f"Bot not found: {bot_id}")
    return bot.value


def get_owned_bot(bot_id: int, twitch_user: Annotated[TwitchUserInfo, Depends(get_owned_twitch_user)]) -> BotConfigDB:
    bot = get_bot_core(bot_id)
    if bot.value is None:
        raise HTTPException(HTTPStatus.NOT_FOUND, f"Bot not found: {bot_id}")

    if bot.value.twitch_user_id != twitch_user.id_:
        raise HTTPException(HTTPStatus.FORBIDDEN, "You are not the owner of this bot")

    return bot.value


def get_owned_alias(alias_id: int, bot: Annotated[BotConfigDB, Depends(get_owned_bot)]) -> AliasDictEntry:
    return _get_owned_ressource(alias_id, get_alias_by_id, bot)


def get_owned_command(command_id: int, bot: Annotated[BotConfigDB, Depends(get_owned_bot)]) -> BasicCommandDB:
    return _get_owned_ressource(command_id, get_command_by_id, bot)


def get_owned_counter(counter_id: int, bot: Annotated[BotConfigDB, Depends(get_owned_bot)]) -> CounterDB:
    return _get_owned_ressource(counter_id, get_counter_by_id, bot)


def get_owned_discord_server(server_id: int, bot: Annotated[BotConfigDB, Depends(get_owned_bot)]) -> DiscordServerDB:
    return _get_owned_ressource(server_id, get_discord_by_server_id, bot)


def get_owned_quote(quote_id: int, bot: Annotated[BotConfigDB, Depends(get_owned_bot)]) -> Quote:
    return _get_owned_ressource(quote_id, get_quote_by_id, bot)


def get_owned_discord_feature_flags(
    feature_flags_id: int, bot: Annotated[BotConfigDB, Depends(get_owned_bot)]
) -> DiscordFeatureFlagsDB:
    return _get_owned_ressource(feature_flags_id, select_discord_feature_flags_by_id, bot)


def get_owned_twitch_feature_flags(
    feature_flags_id: int, bot: Annotated[BotConfigDB, Depends(get_owned_bot)]
) -> TwitchFeatureFlagsDB:
    return _get_owned_ressource(feature_flags_id, select_twitch_feature_flags_by_id, bot)


def get_owned_live_message(
    live_message_id: int, bot: Annotated[BotConfigDB, Depends(get_owned_bot)]
) -> TwitchBroadcastMessageDB:
    return _get_owned_ressource(live_message_id, get_broadcast_message_by_id, bot)


def get_owned_broadcast_message(
    broadcast_message_id: int, bot: Annotated[BotConfigDB, Depends(get_owned_bot)]
) -> TwitchBroadcastMessageDB:
    return _get_owned_ressource(broadcast_message_id, get_broadcast_message_by_id, bot)


def get_owned_twitch_channel(channel_name: str, bot: Annotated[BotConfigDB, Depends(get_owned_bot)]) -> TwitchChannelDB:
    res: Final = get_twitch_channel_by_name(channel_name)

    if res.state.fail or res.value is None:
        raise HTTPException(HTTPStatus.NOT_FOUND, f"{type(res.value).__name__} not found")

    if res.value.bot_id != bot.id:
        raise HTTPException(HTTPStatus.FORBIDDEN, "You are not the owner of this ressource")

    return res.value


class HasBotId(Protocol):
    bot_id: int


def _get_owned_ressource[T: HasBotId](
    resource_id: int,
    callable_: Callable[[int], Result[T]],
    bot: Annotated[BotConfigDB, Depends(get_owned_bot)],
) -> T:
    res: Final = callable_(resource_id)

    if res.state.fail or res.value is None:
        raise HTTPException(HTTPStatus.NOT_FOUND, f"{type(res.value).__name__} not found")

    if res.value.bot_id != bot.id:
        raise HTTPException(HTTPStatus.FORBIDDEN, "You are not the owner of this ressource")

    return res.value
