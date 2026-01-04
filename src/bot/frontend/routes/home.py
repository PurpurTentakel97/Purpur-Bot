from typing import Annotated
from typing import Final
from typing import Optional

from fastapi import APIRouter
from fastapi import Depends
from starlette.requests import Request
from starlette.responses import Response
from starlette.templating import Jinja2Templates

from bot.database.bot import get_bots_by_twitch_id
from bot.frontend.helpers.auth import get_discord_user
from bot.frontend.helpers.auth import get_twitch_user
from bot.frontend.helpers.route_utils import get_templates
from bot.types.discord_user_info import DiscordUserInfo
from bot.types.twitch_user_info import TwitchUserInfo

router: Final = APIRouter()


@router.get("/")
async def home(
    request: Request,
    template: Annotated[Jinja2Templates, Depends(get_templates)],
    twitch_user: Annotated[Optional[TwitchUserInfo], Depends(get_twitch_user)],
    discord_user: Annotated[Optional[DiscordUserInfo], Depends(get_discord_user)],
) -> Response:
    if twitch_user is None:
        return template.TemplateResponse(
            request=request, name="home.html", context={"twitch_user": twitch_user, "discord_user": discord_user}
        )

    bots = get_bots_by_twitch_id(twitch_user.id_) if twitch_user else []

    return template.TemplateResponse(
        request=request,
        name="home.html",
        context={"twitch_user": twitch_user, "discord_user": discord_user, "bots": bots},
    )
