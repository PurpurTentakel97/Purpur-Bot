from http import HTTPStatus
from typing import Annotated
from typing import Final
from typing import Optional

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Form
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.responses import Response
from starlette.templating import Jinja2Templates

from bot.core.broadcast_messages import delete_broadcast_message_by_id as delete_broadcast_message_by_id_core
from bot.core.broadcast_messages import (
    get_broadcast_message_by_channel_name as get_broadcast_message_by_channel_name_core,
)
from bot.core.broadcast_messages import save_broadcast_message as save_broadcast_message_core
from bot.core.broadcast_messages import update_broadcast_message_by_id as update_broadcast_message_by_id_core
from bot.core.twitch import add_twitch_channel as add_twitch_channel_core
from bot.core.twitch import delete_twitch_channel as delete_twitch_channel_core
from bot.core.twitch import get_twitch_channels_from_bot as get_twitch_channels_core
from bot.core.twitch import update_twitch_channel_enabled_by_id as update_twitch_channel_enabled_by_id_core
from bot.core.twitch_feature_flags import (
    select_twitch_feature_flags_by_channel_name as select_twitch_feature_flags_by_channel_name_core,
)
from bot.core.twitch_feature_flags import update_twitch_feature_flags_by_id as update_twitch_feature_flags_by_id_core
from bot.database.types.bot_config import BotConfigDB
from bot.frontend.helpers.auth import get_authenticated_twitch_user
from bot.frontend.helpers.auth import get_discord_user
from bot.frontend.helpers.route_utils import get_templates
from bot.frontend.helpers.route_utils import get_valid_bot
from bot.frontend.helpers.twitch import get_allowed_twitch_channels
from bot.frontend.types.discord_user_info import DiscordUserInfo
from bot.frontend.types.twitch_user_info import TwitchUserInfo

router: Final = APIRouter(prefix="/dashboard/twitch", dependencies=[Depends(get_authenticated_twitch_user)])


# twitch global
@router.get("/{bot_id:int}")
async def dashboard_twitch(
    request: Request,
    bot: Annotated[BotConfigDB, Depends(get_valid_bot)],
    twitch_user: Annotated[TwitchUserInfo, Depends(get_authenticated_twitch_user)],
    discord_user: Annotated[Optional[DiscordUserInfo], Depends(get_discord_user)],
    template: Annotated[Jinja2Templates, Depends(get_templates)],
) -> Response:
    twitch_channels = get_twitch_channels_core(bot.id)
    if twitch_channels.value is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Twitch Channels not found")

    allowed_channels = await get_allowed_twitch_channels(twitch_user.id_, twitch_user.login)
    joined_channel_names = {c.channel_name for c in twitch_channels.value or []}
    filtered_allowed_channels = [c for c in allowed_channels if c.lower() not in joined_channel_names]

    return template.TemplateResponse(
        request=request,
        name="dashboard_twitch.html",
        context={
            "bot": bot,
            "twitch_channels": twitch_channels.value,
            "allowed_channels": filtered_allowed_channels,
            "twitch_user": twitch_user,
            "discord_user": discord_user,
            "active_tab": "channels",
            "plattform": "twitch",
        },
    )


@router.post("/{bot_id:int}")
async def dashboard_twitch_join(
    bot: Annotated[BotConfigDB, Depends(get_valid_bot)], name: Annotated[str, Form()]
) -> RedirectResponse:
    result = await add_twitch_channel_core(bot.id, name)

    if result.state.fail:
        return RedirectResponse(
            url=f"/dashboard/twitch/{bot.id}?error_message=Failed to add twitch channel | reason: {result.state.name}",
            status_code=HTTPStatus.SEE_OTHER,
        )

    return RedirectResponse(
        url=f"/dashboard/twitch/{bot.id}?success_message=Twitch channel added successfully",
        status_code=HTTPStatus.SEE_OTHER,
    )


@router.post("/delete/{bot_id:int}/{name:str}")
async def dashboard_twitch_delete(
    bot_id: int,
    name: str,
) -> RedirectResponse:
    result = await delete_twitch_channel_core(bot_id, name)

    if result.state.fail:
        return RedirectResponse(
            url=f"/dashboard/twitch/{bot_id}?error_message=Failed to delete twitch channel "
            + f"| reason: {result.state.name}",
            status_code=HTTPStatus.SEE_OTHER,
        )

    return RedirectResponse(
        url=f"/dashboard/twitch/{bot_id}?success_message=Twitch channel deleted successfully",
        status_code=HTTPStatus.SEE_OTHER,
    )


# channel
@router.get("/{bot_id:int}/channel/{name:str}")
async def dashboard_twitch_channel(
    request: Request,
    name: str,
    bot: Annotated[BotConfigDB, Depends(get_valid_bot)],
    twitch_user: Annotated[TwitchUserInfo, Depends(get_authenticated_twitch_user)],
    discord_user: Annotated[Optional[DiscordUserInfo], Depends(get_discord_user)],
    template: Annotated[Jinja2Templates, Depends(get_templates)],
) -> Response:
    twitch_channels = get_twitch_channels_core(bot.id)
    if twitch_channels.value is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Twitch Channels not found")

    twitch_feature_flags = select_twitch_feature_flags_by_channel_name_core(bot.id, name)
    if twitch_feature_flags.value is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Twitch Feature Flags not found")

    broadcast_message = get_broadcast_message_by_channel_name_core(bot.id, name)
    if broadcast_message.value is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Broadcast Message not found")

    return template.TemplateResponse(
        request=request,
        name="dashboard_twitch_channel.html",
        context={
            "bot": bot,
            "twitch_user": twitch_user,
            "discord_user": discord_user,
            "name": name,
            "twitch_channels": twitch_channels.value,
            "active_channel": name,
            "feature_flags": twitch_feature_flags.value,
            "broadcast_message": broadcast_message.value,
        },
    )


@router.post("/{bot_id:int}/{name:str}/feature_flags/{feature_flag_id:int}")
async def dashboard_twitch_feature_flag_update(
    bot: Annotated[BotConfigDB, Depends(get_valid_bot)],
    name: str,
    feature_flag_id: int,
    can_commands: Annotated[bool, Form()] = False,
    can_alias: Annotated[bool, Form()] = False,
    can_broadcast: Annotated[bool, Form()] = False,
) -> RedirectResponse:
    result = update_twitch_feature_flags_by_id_core(feature_flag_id, can_commands, can_alias, can_broadcast)

    if result.state.fail:
        return RedirectResponse(
            url=f"/dashboard/twitch/{bot.id}/channel/{name}?error_message=Failed to update twitch feature flags "
            + f"| reason: {result.state.name}",
            status_code=HTTPStatus.SEE_OTHER,
        )

    return RedirectResponse(
        url=f"/dashboard/twitch/{bot.id}/channel/{name}?success_message=Twitch feature flags updated successfully",
        status_code=HTTPStatus.SEE_OTHER,
    )


@router.post("/{bot_id:int}/{name:str}/channel/update/{channel_id:int}")
async def dashboard_twitch_channel_update(
    bot: Annotated[BotConfigDB, Depends(get_valid_bot)],
    name: str,
    channel_id: int,
    enabled: Annotated[bool, Form()] = False,
) -> RedirectResponse:
    result = update_twitch_channel_enabled_by_id_core(channel_id, enabled)

    if result.state.fail:
        return RedirectResponse(
            url=f"/dashboard/twitch/{bot.id}/channel/{name}?error_message=Failed to update twitch channel "
            + f"| reason: {result.state.name}",
            status_code=HTTPStatus.SEE_OTHER,
        )

    return RedirectResponse(
        url=f"/dashboard/twitch/{bot.id}/channel/{name}?success_message=Twitch channel updated successfully",
        status_code=HTTPStatus.SEE_OTHER,
    )


# broadcast messages
@router.post("/{bot_id:int}/{name:str}/broadcast_message/save")
async def dashboard_twitch_broadcast_message_save(
    bot: Annotated[BotConfigDB, Depends(get_valid_bot)],
    name: str,
    message: Annotated[str, Form()],
    interval: Annotated[int, Form()],
) -> RedirectResponse:
    result = save_broadcast_message_core(bot.id, name, message, interval)

    if result.state.fail:
        return RedirectResponse(
            url=f"/dashboard/twitch/{bot.id}/channel/{name}?error_message=Failed to save broadcast message "
            + f"| reason: {result.state.name}",
            status_code=HTTPStatus.SEE_OTHER,
        )

    return RedirectResponse(
        url=f"/dashboard/twitch/{bot.id}/channel/{name}?success_message=Broadcast message saved successfully",
        status_code=HTTPStatus.SEE_OTHER,
    )


@router.post("/{bot_id:int}/{name:str}/broadcast_message/update/{message_id:int}")
def update_broadcast_message(
    bot: Annotated[BotConfigDB, Depends(get_valid_bot)],
    name: str,
    message_id: int,
    message: Annotated[str, Form()],
    interval: Annotated[int, Form()],
    enabled: Annotated[bool, Form()] = False,
) -> RedirectResponse:
    result = update_broadcast_message_by_id_core(message_id, message, interval, enabled)

    if result.state.fail:
        return RedirectResponse(
            url=f"/dashboard/twitch/{bot.id}/channel/{name}?error_message=Failed to update broadcast message "
            + f"| reason: {result.state.name}",
            status_code=HTTPStatus.SEE_OTHER,
        )

    return RedirectResponse(
        url=f"/dashboard/twitch/{bot.id}/channel/{name}?success_message=Broadcast message updated successfully",
        status_code=HTTPStatus.SEE_OTHER,
    )


@router.post("/{bot_id:int}/{name:str}/broadcast_message/delete/{message_id:int}")
def delete_broadcast_message(
    bot: Annotated[BotConfigDB, Depends(get_valid_bot)], name: str, message_id: int
) -> RedirectResponse:
    result = delete_broadcast_message_by_id_core(message_id)

    if result.state.fail:
        return RedirectResponse(
            url=f"/dashboard/twitch/{bot.id}/channel/{name}?error_message=Failed to delete broadcast message "
            + f"| reason: {result.state.name}",
            status_code=HTTPStatus.SEE_OTHER,
        )

    return RedirectResponse(
        url=f"/dashboard/twitch/{bot.id}/channel/{name}?success_message=Broadcast message deleted successfully",
        status_code=HTTPStatus.SEE_OTHER,
    )
