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
from bot.core.discord import get_discord_by_server_id as get_discord_by_server_id_core
from bot.core.discord import get_discord_servers_by_bot_id as get_discord_servers_by_bot_id_core
from bot.core.discord_feature_flags import (
    select_discord_feature_flags_by_server_id as select_discord_feature_flags_by_server_id_core,
)
from bot.core.discord_feature_flags import (
    update_discord_feature_flags_by_id as update_discord_feature_flags_by_id_core,
)
from bot.database.types.bot_config import BotConfigDB
from bot.frontend.helpers.auth import get_authenticated_discord_user
from bot.frontend.helpers.auth import get_authenticated_twitch_user
from bot.frontend.helpers.discord import get_allowed_discord_servers
from bot.frontend.helpers.route_utils import get_templates
from bot.frontend.helpers.route_utils import get_valid_bot
from bot.frontend.types.discord_user_info import DiscordUserInfo
from bot.frontend.types.twitch_user_info import TwitchUserInfo

router: Final = APIRouter(
    prefix="/dashboard/discord",
    dependencies=[Depends(get_authenticated_twitch_user), Depends(get_authenticated_discord_user)],
)


@router.get("/{bot_id:int}")
async def dashboard_discord(
    request: Request,
    bot: Annotated[BotConfigDB, Depends(get_valid_bot)],
    discord_user: Annotated[DiscordUserInfo, Depends(get_authenticated_discord_user)],
    twitch_user: Annotated[TwitchUserInfo, Depends(get_authenticated_twitch_user)],
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
    bot: Annotated[BotConfigDB, Depends(get_valid_bot)],
    server_id: Annotated[int, Form()],
    discord_user: Annotated[DiscordUserInfo, Depends(get_authenticated_discord_user)],
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
    bot_id: int,
    server_id: int,
) -> RedirectResponse:
    result = await delete_discord_bot_core(bot_id, server_id)

    if result.state.fail:
        return RedirectResponse(
            url=f"/dashboard/discord/{bot_id}?error_message=Failed to delete discord server "
            + f"| reason: {result.state.name}",
            status_code=HTTPStatus.SEE_OTHER,
        )

    return RedirectResponse(
        url=f"/dashboard/discord/{bot_id}?success_message=Discord server deleted successfully",
        status_code=HTTPStatus.SEE_OTHER,
    )


@router.get("/{bot_id:int}/server/{server_id:int}")
async def dashboard_discord_server(
    request: Request,
    server_id: int,
    bot: Annotated[BotConfigDB, Depends(get_valid_bot)],
    discord_user: Annotated[DiscordUserInfo, Depends(get_authenticated_discord_user)],
    twitch_user: Annotated[TwitchUserInfo, Depends(get_authenticated_twitch_user)],
    template: Annotated[Jinja2Templates, Depends(get_templates)],
) -> Response:
    server = get_discord_by_server_id_core(server_id)
    if server.value is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Discord Server not found")
    discord_servers = get_discord_servers_by_bot_id_core(bot.id)
    if discord_servers.value is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Discord Servers not found")

    discord_feature_flags = select_discord_feature_flags_by_server_id_core(bot.id, str(server_id))
    if discord_feature_flags.value is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Discord Feature Flags not found")

    return template.TemplateResponse(
        request=request,
        name="dashboard_discord_server.html",
        context={
            "bot": bot,
            "twitch_user": twitch_user,
            "discord_user": discord_user,
            "server": server.value,
            "discord_server": discord_servers.value,
            "active_tab": server_id,
            "feature_flags": discord_feature_flags.value,
        },
    )


@router.post("/{bot_id:int}/{server_id:int}/feature_flags/{feature_flag_id:int}")
async def dashboard_discord_feature_flag_update(
    bot: Annotated[BotConfigDB, Depends(get_valid_bot)],
    server_id: int,
    feature_flag_id: int,
    can_commands: Annotated[bool, Form()] = False,
    can_alias: Annotated[bool, Form()] = False,
) -> RedirectResponse:
    result = update_discord_feature_flags_by_id_core(feature_flag_id, can_commands, can_alias)

    if result.state.fail:
        return RedirectResponse(
            url=f"/dashboard/discord/{bot.id}/server/{server_id}?error_message=Failed to update discord feature flags "
            + f"| reason: {result.state.name}",
            status_code=HTTPStatus.SEE_OTHER,
        )

    return RedirectResponse(
        url=f"/dashboard/discord/{bot.id}/server/{server_id}?success_message=Discord feature flags updated successfully",
        status_code=HTTPStatus.SEE_OTHER,
    )
