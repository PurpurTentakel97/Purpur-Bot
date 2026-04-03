from http import HTTPStatus
from typing import Annotated
from typing import Final

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Form
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.responses import Response
from starlette.templating import Jinja2Templates

from bot.core.app_context import APP_CONTEXT
from bot.core.discord import add_discord_bot as add_discord_bot_core
from bot.core.discord import delete_discord_bot as delete_discord_bot_core
from bot.core.discord import get_discord_servers_by_bot_id as get_discord_servers_by_bot_id_core
from bot.core.discord import update_discord_enabled_by_id as update_discord_enabled_by_id_core
from bot.core.discord_feature_flags import (
    select_discord_feature_flags_by_server_id as select_discord_feature_flags_by_server_id_core,
)
from bot.core.discord_feature_flags import update_discord_feature_flags_by_id as update_discord_feature_flags_by_id_core
from bot.core.twitch_event_hub_management import add_twitch_event_hub_entry as add_twitch_event_hub_entry_core
from bot.core.twitch_event_hub_management import delete_twitch_event_hub_entry as delete_twitch_event_hub_entry_core
from bot.core.twitch_event_hub_management import (
    send_test_twitch_event_hub_entry as send_test_twitch_event_hub_entry_core,
)
from bot.core.twitch_event_hub_management import update_twitch_event_hub as update_twitch_event_hub_core
from bot.database.twitch_event_hub import (
    select_twitch_event_hubs_by_server_id as select_twitch_event_hubs_by_server_id_db,
)
from bot.database.types.bot_config import BotConfigDB
from bot.database.types.discord_server import DiscordServerDB
from bot.database.types.feature_flags import DiscordFeatureFlagsDB
from bot.database.types.twitch_broadcast_message import TwitchBroadcastMessageDB
from bot.frontend.helpers.decorators import get_owned_bot
from bot.frontend.helpers.decorators import get_owned_discord_feature_flags
from bot.frontend.helpers.decorators import get_owned_discord_server
from bot.frontend.helpers.decorators import get_owned_discord_user
from bot.frontend.helpers.decorators import get_owned_live_message
from bot.frontend.helpers.decorators import get_owned_twitch_user
from bot.frontend.helpers.discord import get_allowed_discord_servers
from bot.frontend.helpers.discord import get_discord_channels
from bot.frontend.helpers.route_utils import get_templates
from bot.frontend.types.discord_user_info import DiscordUserInfo
from bot.frontend.types.twitch_user_info import TwitchUserInfo

router: Final = APIRouter(
    prefix="/dashboard/discord",
    dependencies=[Depends(get_owned_twitch_user), Depends(get_owned_discord_user)],
)


@router.get("/{bot_id:int}")
async def dashboard_discord(
    request: Request,
    bot: Annotated[BotConfigDB, Depends(get_owned_bot)],
    discord_user: Annotated[DiscordUserInfo, Depends(get_owned_discord_user)],
    twitch_user: Annotated[TwitchUserInfo, Depends(get_owned_twitch_user)],
    template: Annotated[Jinja2Templates, Depends(get_templates)],
) -> Response:
    discord_servers = get_discord_servers_by_bot_id_core(bot.id)
    if discord_servers.value is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Discord Servers not found")
    allowed_discord_servers = await get_allowed_discord_servers(discord_user.id_)

    # Filter allowed_discord_servers to only include those that are not yet in discord_servers
    joined_server_ids = {s.server_id for s in discord_servers.value or []}
    filtered_allowed_discord_servers = [s for s in allowed_discord_servers if int(s["id"]) not in joined_server_ids]

    invite_links: dict[int, str] = {}
    for server in discord_servers.value:
        client_id = APP_CONTEXT.discord_client_id.value_unsafe() or ""
        permissions = 8  # Administrator
        invite_link = (
            f"https://discord.com/api/oauth2/authorize?client_id={client_id}&permissions={permissions}"
            + f"&scope=bot&guild_id={server.server_id}&disable_guild_select=true"
        )
        invite_links[server.server_id] = invite_link

    return template.TemplateResponse(
        request=request,
        name="dashboard_discord.html",
        context={
            "bot": bot,
            "discord_server": discord_servers.value,
            "allowed_server": filtered_allowed_discord_servers,
            "invite_links": invite_links,
            "twitch_user": twitch_user,
            "discord_user": discord_user,
            "active_tab": "server",
            "plattform": "discord",
        },
    )


@router.post("/{bot_id:int}")
async def dashboard_discord_join(
    bot: Annotated[BotConfigDB, Depends(get_owned_bot)],
    server_id: Annotated[int, Form()],
    discord_user: Annotated[DiscordUserInfo, Depends(get_owned_discord_user)],
) -> RedirectResponse:
    allowed_servers = await get_allowed_discord_servers(discord_user.id_)
    server_name = next((s["name"] for s in allowed_servers if int(s["id"]) == server_id), "Unknown")

    result = add_discord_bot_core(bot.id, server_id, server_name)

    if result.state.fail:
        return RedirectResponse(
            url=f"/dashboard/discord/{bot.id}?error_message=Failed to add discord server | reason: {result.state.name}",
            status_code=HTTPStatus.SEE_OTHER,
        )

    return RedirectResponse(
        url=f"/dashboard/discord/{bot.id}?success_message=Discord server added successfully."
        + " Press the 'invite' Button if the bot did not join the server yet.",
        status_code=HTTPStatus.SEE_OTHER,
    )


@router.post("/delete/{bot_id:int}/{server_id:int}")
async def dashboard_discord_delete(
    request: Request,
    bot: Annotated[BotConfigDB, Depends(get_owned_bot)],
    server: Annotated[DiscordServerDB, Depends(get_owned_discord_server)],
) -> RedirectResponse:
    result = await delete_discord_bot_core(bot.id, server.server_id)

    referer = request.headers.get("referer")
    if referer and f"/dashboard/discord/{bot.id}/server/{server.id}" in referer:
        url = f"/dashboard/discord/{bot.id}"
    else:
        url = referer or f"/dashboard/discord/{bot.id}"

    if result.state.fail:
        separator = "&" if "?" in url else "?"
        return RedirectResponse(
            url=f"{url}{separator}error_message=Failed to delete discord server | reason: {result.state.name}",
            status_code=HTTPStatus.SEE_OTHER,
        )

    separator = "&" if "?" in url else "?"
    return RedirectResponse(
        url=f"{url}{separator}success_message=Discord server deleted successfully",
        status_code=HTTPStatus.SEE_OTHER,
    )


@router.get("/{bot_id:int}/server/{server_id:int}")
async def dashboard_discord_server(
    request: Request,
    server: Annotated[DiscordServerDB, Depends(get_owned_discord_server)],
    bot: Annotated[BotConfigDB, Depends(get_owned_bot)],
    discord_user: Annotated[DiscordUserInfo, Depends(get_owned_discord_user)],
    twitch_user: Annotated[TwitchUserInfo, Depends(get_owned_twitch_user)],
    template: Annotated[Jinja2Templates, Depends(get_templates)],
) -> Response:
    discord_servers = get_discord_servers_by_bot_id_core(bot.id)
    if discord_servers.value is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Discord Servers not found")

    discord_feature_flags = select_discord_feature_flags_by_server_id_core(bot.id, server.server_id)
    if discord_feature_flags.value is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Discord Feature Flags not found")

    discord_channels = get_discord_channels(server.server_id)
    twitch_event_hubs = select_twitch_event_hubs_by_server_id_db(server.server_id)

    # Resolve IDs to Names for the table
    channel_names = {c["id"]: c["name"] for c in discord_channels}
    broadcaster_names: dict[str, str] = {}
    broadcaster_logins: dict[str, str] = {}
    if twitch_event_hubs.value and APP_CONTEXT.twitch_client_id.is_valid():
        from bot.core.types.programm_parts import PROGRAMM_PARTS

        if PROGRAMM_PARTS.twitch is not None:
            broadcaster_ids = [hub.broadcaster_id for hub in twitch_event_hubs.value]
            if broadcaster_ids:
                async for user in PROGRAMM_PARTS.twitch.client.get_users(user_ids=broadcaster_ids):
                    broadcaster_names[user.id] = user.display_name or user.login
                    broadcaster_logins[user.id] = user.login

    return template.TemplateResponse(
        request=request,
        name="dashboard_discord_server.html",
        context={
            "bot": bot,
            "twitch_user": twitch_user,
            "discord_user": discord_user,
            "server": server,
            "discord_server": discord_servers.value,
            "active_tab": server.server_id,
            "feature_flags": discord_feature_flags.value,
            "discord_channels": discord_channels,
            "twitch_event_hubs": twitch_event_hubs.value,
            "channel_names": channel_names,
            "broadcaster_names": broadcaster_names,
            "broadcaster_logins": broadcaster_logins,
        },
    )


@router.post("/{bot_id:int}/{server_id:int}/feature_flags/{feature_flags_id:int}")
async def dashboard_discord_feature_flag_update(
    bot: Annotated[BotConfigDB, Depends(get_owned_bot)],
    server: Annotated[DiscordServerDB, Depends(get_owned_discord_server)],
    feature_flags: Annotated[DiscordFeatureFlagsDB, Depends(get_owned_discord_feature_flags)],
    can_commands: Annotated[bool, Form()] = False,
    can_alias: Annotated[bool, Form()] = False,
    can_twitch_live: Annotated[bool, Form()] = False,
    can_quote: Annotated[bool, Form()] = False,
) -> RedirectResponse:
    result = update_discord_feature_flags_by_id_core(
        feature_flags.id,
        can_commands,
        can_alias,
        can_twitch_live,
        can_quote,
    )

    if result.state.fail:
        return RedirectResponse(
            url=f"/dashboard/discord/{bot.id}/server/{server.server_id}"
            + "?error_message=Failed to update discord feature flags "
            + f"| reason: {result.state.name}",
            status_code=HTTPStatus.SEE_OTHER,
        )

    return RedirectResponse(
        url=f"/dashboard/discord/{bot.id}/server/{server.server_id}"
        + "?success_message=Discord feature flags updated successfully",
        status_code=HTTPStatus.SEE_OTHER,
    )


@router.post("/{bot_id:int}/{server_id:int}/server/update/{discord_id:int}")
async def dashboard_discord_server_update(
    request: Request,
    bot: Annotated[BotConfigDB, Depends(get_owned_bot)],
    server: Annotated[DiscordServerDB, Depends(get_owned_discord_server)],
    server_2: Annotated[DiscordServerDB, Depends(get_owned_discord_server)],
    enabled: Annotated[bool, Form()] = False,
) -> RedirectResponse:
    result = await update_discord_enabled_by_id_core(server_2.id, enabled)

    referer = request.headers.get("referer")
    url = referer or f"/dashboard/discord/{bot.id}/server/{server.server_id}"

    if result.state.fail:
        separator = "&" if "?" in url else "?"
        return RedirectResponse(
            url=f"{url}{separator}error_message=Failed to update discord server | reason: {result.state.name}",
            status_code=HTTPStatus.SEE_OTHER,
        )

    separator = "&" if "?" in url else "?"
    return RedirectResponse(
        url=f"{url}{separator}success_message=Discord server updated successfully",
        status_code=HTTPStatus.SEE_OTHER,
    )


@router.post("/{bot_id:int}/{server_id:int}/live_message/save")
async def dashboard_discord_live_message_save(
    bot: Annotated[BotConfigDB, Depends(get_owned_bot)],
    server: Annotated[DiscordServerDB, Depends(get_owned_discord_server)],
    discord_channel_id: Annotated[int, Form()],
    broadcaster_id: Annotated[str, Form()],
    message: Annotated[str, Form()],
) -> RedirectResponse:
    result = await add_twitch_event_hub_entry_core(
        bot_id=bot.id,
        server_id=server.server_id,
        channel_id=discord_channel_id,
        broadcaster_id=broadcaster_id,
        message=message,
    )

    if result.state.fail:
        return RedirectResponse(
            url=f"/dashboard/discord/{bot.id}/server/{server.server_id}"
            + f"?error_message=Failed to save discord live message | reason: {result.state.name}",
            status_code=HTTPStatus.SEE_OTHER,
        )

    return RedirectResponse(
        url=f"/dashboard/discord/{bot.id}/server/{server.server_id}"
        + "?success_message=Discord live message saved successfully",
        status_code=HTTPStatus.SEE_OTHER,
    )


@router.post("/{bot_id:int}/{server_id:int}/live_message/update/{live_message_id:int}")
async def dashboard_discord_live_message_update(
    bot: Annotated[BotConfigDB, Depends(get_owned_bot)],
    server: Annotated[DiscordServerDB, Depends(get_owned_discord_server)],
    live_message: Annotated[TwitchBroadcastMessageDB, Depends(get_owned_live_message)],
    discord_channel_id: Annotated[int, Form()],
    message: Annotated[str, Form()],
    enabled: Annotated[bool, Form()] = False,
) -> RedirectResponse:
    result = await update_twitch_event_hub_core(live_message.id, discord_channel_id, message, enabled)

    if result.state.fail:
        return RedirectResponse(
            url=f"/dashboard/discord/{bot.id}/server/{server.server_id}"
            + f"?error_message=Failed to update discord live message | reason: {result.state.name}",
            status_code=HTTPStatus.SEE_OTHER,
        )

    return RedirectResponse(
        url=f"/dashboard/discord/{bot.id}/server/{server.server_id}"
        + "?success_message=Discord live message updated successfully",
        status_code=HTTPStatus.SEE_OTHER,
    )


@router.post("/{bot_id:int}/{server_id:int}/live_message/delete/{live_message_id:int}")
async def dashboard_discord_live_message_delete(
    bot: Annotated[BotConfigDB, Depends(get_owned_bot)],
    server: Annotated[DiscordServerDB, Depends(get_owned_discord_server)],
    live_message: Annotated[TwitchBroadcastMessageDB, Depends(get_owned_live_message)],
) -> RedirectResponse:
    result = await delete_twitch_event_hub_entry_core(live_message.id)

    if result.state.fail:
        return RedirectResponse(
            url=f"/dashboard/discord/{bot.id}/server/{server.server_id}"
            + f"?error_message=Failed to delete discord live message | reason: {result.state.name}",
            status_code=HTTPStatus.SEE_OTHER,
        )

    return RedirectResponse(
        url=f"/dashboard/discord/{bot.id}/server/{server.server_id}?"
        + "success_message=Discord live message deleted successfully",
        status_code=HTTPStatus.SEE_OTHER,
    )


@router.post("/{bot_id:int}/{server_id:int}/live_message/test/{live_message_id:int}")
async def dashboard_discord_live_message_test(
    bot: Annotated[BotConfigDB, Depends(get_owned_bot)],
    server: Annotated[DiscordServerDB, Depends(get_owned_discord_server)],
    live_message: Annotated[TwitchBroadcastMessageDB, Depends(get_owned_live_message)],
) -> RedirectResponse:
    result = await send_test_twitch_event_hub_entry_core(live_message.id)

    if result.state.fail:
        return RedirectResponse(
            url=f"/dashboard/discord/{bot.id}/server/{server.server_id}"
            + f"?error_message=Failed to send test discord live message | reason: {result.state.name}",
            status_code=HTTPStatus.SEE_OTHER,
        )

    return RedirectResponse(
        url=f"/dashboard/discord/{bot.id}/server/{server.server_id}"
        + "?success_message=Test discord live message sent successfully",
        status_code=HTTPStatus.SEE_OTHER,
    )
