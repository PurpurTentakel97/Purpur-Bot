from enum import Enum
from enum import auto
from http import HTTPStatus
from typing import Annotated
from typing import Any
from typing import Final
from typing import Protocol

from attr import dataclass
from fastapi import Depends
from fastapi import HTTPException
from fastapi_decorators import Decorator
from fastapi_decorators import depends

from bot.core.alias_dict import get_alias_by_id
from bot.core.bot import get_bot
from bot.core.broadcast_messages import get_broadcast_message_by_id
from bot.core.commands import get_command_by_id
from bot.core.counter import get_counter_by_id
from bot.core.discord import get_discord_by_server_id
from bot.core.discord_feature_flags import select_discord_feature_flags_by_id
from bot.core.quote import get_quote_by_id
from bot.core.twitch import get_twitch_channel_by_id
from bot.core.twitch import get_twitch_channel_by_name
from bot.core.twitch_event_hub_management import get_twitch_event_hub_by_id
from bot.core.twitch_feature_flags import select_twitch_feature_flags_by_id
from bot.core.types.result import Result
from bot.core.types.result import ResultState
from bot.frontend.helpers.auth import get_authenticated_twitch_user
from bot.frontend.types.twitch_user_info import TwitchUserInfo


class ResourceType(Enum):
    BOT = auto()
    ALIAS = auto()
    COMMAND = auto()
    COUNTER = auto()
    QUOTE = auto()
    TWITCH_FEATURE_FLAG = auto()
    TWITCH_CHANNEL = auto()
    BROADCAST_MESSAGE = auto()
    DISCORD_SERVER = auto()
    DISCORD_FEATURE_FLAGS = auto()
    LIVE_MESSAGE = auto()


@dataclass
class _SimpleBot:
    bot_id: int


class _HasBotId(Protocol):
    bot_id: int


def _bot_id_dummy(resource_id: int) -> Result[_HasBotId]:
    return Result(ResultState.SUCCESS, _SimpleBot(resource_id))


_function_lookup: Final = {
    ResourceType.BOT: _bot_id_dummy,
    ResourceType.ALIAS: get_alias_by_id,
    ResourceType.COMMAND: get_command_by_id,
    ResourceType.COUNTER: get_counter_by_id,
    ResourceType.QUOTE: get_quote_by_id,
    ResourceType.TWITCH_FEATURE_FLAG: select_twitch_feature_flags_by_id,
    ResourceType.TWITCH_CHANNEL: get_twitch_channel_by_id,
    ResourceType.BROADCAST_MESSAGE: get_broadcast_message_by_id,
    ResourceType.DISCORD_SERVER: get_discord_by_server_id,
    ResourceType.DISCORD_FEATURE_FLAGS: select_discord_feature_flags_by_id,
    ResourceType.LIVE_MESSAGE: get_twitch_event_hub_by_id,
}


async def _valide_resource_owner(resource_id: int, resource_type: ResourceType, twitch_user: TwitchUserInfo) -> None:
    result: Result[Any] = _function_lookup[resource_type](resource_id)
    res: Result[_HasBotId] = _function_lookup[resource_type](resource_id).cast_to(_HasBotId, result.value)
    bot_id = res.value.bot_id if res.value else None

    if bot_id is None:
        raise HTTPException(
            HTTPStatus.INTERNAL_SERVER_ERROR, f"Failed to fetch bot_id with resource_type: {resource_type}"
        )

    bot = get_bot(bot_id)
    if bot.value is None:
        raise HTTPException(HTTPStatus.NOT_FOUND, f"Bot not found: {bot_id}")

    if bot.value.twitch_user_id != twitch_user.id_:
        raise HTTPException(HTTPStatus.FORBIDDEN, "You are not the owner of this resource")


def resource_owner_required(
    resource_type: ResourceType,
) -> Decorator:
    @depends
    async def wrapper(
        resource_id: int,
        twitch_user: Annotated[TwitchUserInfo, Depends(get_authenticated_twitch_user)],
    ) -> None:
        await _valide_resource_owner(resource_id, resource_type, twitch_user)

    return wrapper


def bot_owner_required() -> Decorator:
    @depends
    async def wrapper(
        bot_id: int,
        twitch_user: Annotated[TwitchUserInfo, Depends(get_authenticated_twitch_user)],
    ) -> None:
        await _valide_resource_owner(bot_id, ResourceType.BOT, twitch_user)

    return wrapper


def twitch_channel_owner_required() -> Decorator:
    @depends
    async def wrapper(
        name: str,
        twitch_user: Annotated[TwitchUserInfo, Depends(get_authenticated_twitch_user)],
    ) -> None:
        channel = get_twitch_channel_by_name(name)
        if channel.value is None:
            raise HTTPException(HTTPStatus.NOT_FOUND, f"Channel not found: {name}")

        bot = get_bot(channel.value.bot_id)
        if bot.value is None:
            raise HTTPException(HTTPStatus.NOT_FOUND, f"Bot not found: {channel.value.bot_id}")

        if bot.value.twitch_user_id != twitch_user.id_:
            raise HTTPException(HTTPStatus.FORBIDDEN, "You are not the owner of this resource")

    return wrapper
