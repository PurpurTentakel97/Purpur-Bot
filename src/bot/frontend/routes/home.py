from typing import Annotated
from typing import Final
from typing import Optional

from fastapi import APIRouter
from fastapi import Depends
from starlette.requests import Request
from starlette.responses import Response
from starlette.templating import Jinja2Templates

from bot.database.bot import get_bots_by_twitch_id
from bot.frontend.helpers.auth import get_twitch_user
from bot.frontend.helpers.route_utils import get_templates
from bot.helpers.log import LogLevel
from bot.helpers.log import log_default
from bot.types.twitch_user_info import TwitchUserInfo

router: Final = APIRouter()


@router.get("/")
async def home(
    request: Request,
    template: Annotated[Jinja2Templates, Depends(get_templates)],
    twitch_user: Annotated[Optional[TwitchUserInfo], Depends(get_twitch_user)],
) -> Response:
    if twitch_user is None:
        return template.TemplateResponse(request=request, name="home.html")

    bots = get_bots_by_twitch_id(twitch_user.id_)
    log_default(LogLevel.DEBUG, f"Loaded {len(bots)} bots for twitch user {twitch_user.id_} | Bots: {bots}")

    return template.TemplateResponse(request=request, name="home.html", context={"user": twitch_user, "bots": bots})
