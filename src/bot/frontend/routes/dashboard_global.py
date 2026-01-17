from typing import Annotated, Optional
from fastapi import APIRouter, Depends
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import Response
from starlette.templating import Jinja2Templates

from bot.frontend.helpers.auth import get_authenticated_twitch_user, get_discord_user
from bot.frontend.helpers.route_utils import get_templates
from bot.frontend.types.discord_user_info import DiscordUserInfo
from bot.frontend.types.twitch_user_info import TwitchUserInfo
from bot.core.bot import get_bot as get_bot_core

router = APIRouter(prefix="/dashboard/global", dependencies=[Depends(get_authenticated_twitch_user)])


@router.get("/{bot_id:int}")
async def dashboard_main(
    request: Request,
    bot_id: int,
    twitch_user: Annotated[TwitchUserInfo, Depends(get_authenticated_twitch_user)],
    discord_user: Annotated[Optional[DiscordUserInfo], Depends(get_discord_user)],
    template: Annotated[Jinja2Templates, Depends(get_templates)],
) -> Response:
    bot = get_bot_core(bot_id)
    if bot.value is None:
        raise HTTPException(status_code=404, detail="Bot not found")

    return template.TemplateResponse(
        request=request,
        name="dashboard_global.html",
        context={
            "bot": bot.value,
            "twitch_user": twitch_user,
            "discord_user": discord_user,
        },
    )
