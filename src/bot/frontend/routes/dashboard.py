from typing import Annotated
from typing import Final
from typing import Optional

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from starlette.requests import Request
from starlette.responses import Response
from starlette.templating import Jinja2Templates

from bot.core.bot import get_bot as get_bot_core
from bot.core.commands import get_commands_by_bot_id as get_commands_by_bot_id_core
from bot.core.counter import get_counters_by_bot_id as get_counter_by_bot_id_core
from bot.core.discord import get_discord_servers_by_bot_id as get_discord_servers_by_bot_id_core
from bot.core.twitch import get_twitch_channels_from_bot as get_twitch_channels_core
from bot.frontend.helpers.auth import get_authenticated_twitch_user
from bot.frontend.helpers.auth import get_discord_user
from bot.frontend.helpers.cast import to_int_or_raise
from bot.frontend.helpers.discord import get_allowed_discord_servers
from bot.frontend.helpers.route_utils import get_templates
from bot.frontend.helpers.twitch import get_allowed_twitch_channels
from bot.frontend.types.discord_user_info import DiscordUserInfo
from bot.frontend.types.twitch_user_info import TwitchUserInfo

router: Final = APIRouter(prefix="/dashboard", dependencies=[Depends(get_authenticated_twitch_user)])


@router.get("/bot/edit")
async def bot_dashboard(
    request: Request,
    template: Annotated[Jinja2Templates, Depends(get_templates)],
    current_twitch_user: Annotated[TwitchUserInfo, Depends(get_authenticated_twitch_user)],
    current_discord_user: Annotated[Optional[DiscordUserInfo], Depends(get_discord_user)],
) -> Response:
    data = await request.json()
    bot_id = to_int_or_raise(data.get("bot_id"))

    bot = get_bot_core(bot_id)
    if bot.value is None:
        raise HTTPException(status_code=404, detail="Bot not found")

    twitch_channels = get_twitch_channels_core(bot_id)
    if twitch_channels.value is None:
        raise HTTPException(status_code=404, detail="Twitch Channels not found")

    allowed_channels = await get_allowed_twitch_channels(current_twitch_user.id_, current_twitch_user.login)

    # filter allowed_channels to only include those that are not yet in twitch_channels
    joined_channel_names = {c.channel_name for c in twitch_channels.value or []}
    filtered_allowed_channels = [c for c in allowed_channels if c.lower() not in joined_channel_names]

    commands = get_commands_by_bot_id_core(bot_id)
    if commands.value is None:
        raise HTTPException(status_code=404, detail="Commands not found")
    counters = get_counter_by_bot_id_core(bot_id)
    if counters.value is None:
        raise HTTPException(status_code=404, detail="Counters not found")

    discord_servers = get_discord_servers_by_bot_id_core(bot_id)
    if discord_servers.value is None:
        raise HTTPException(status_code=404, detail="Discord Servers not found")
    allowed_discord_servers = (
        await get_allowed_discord_servers(current_discord_user.id_) if current_discord_user else []
    )

    # Filter allowed_discord_servers to only include those that are not yet in discord_servers
    joined_server_ids = {s.server_id for s in discord_servers.value or []}
    filtered_allowed_discord_servers = [s for s in allowed_discord_servers if int(s["id"]) not in joined_server_ids]

    return template.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "bot": bot,
            "twitch_channels": twitch_channels,
            "allowed_channels": filtered_allowed_channels,
            "commands": commands,
            "counters": counters,
            "twitch_user": current_twitch_user,
            "discord_user": current_discord_user,
            "discord_servers": discord_servers,
            "allowed_discord_servers": filtered_allowed_discord_servers,
        },
    )
