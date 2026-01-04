from typing import Annotated
from typing import Final

from fastapi import APIRouter
from fastapi import Depends
from starlette.requests import Request
from starlette.responses import Response
from starlette.templating import Jinja2Templates
from twitchAPI.object.api import TwitchUser

from bot.frontend.helpers.auth import get_authenticated_twitch_user
from bot.frontend.helpers.route_utils import get_templates

router: Final = APIRouter(prefix="/dashboard", dependencies=[Depends(get_authenticated_twitch_user)])


@router.get("/bot/{bot_id:int}")
def bot_dashboard(
    request: Request,
    template: Annotated[Jinja2Templates, Depends(get_templates)],
    current_twitch_user: Annotated[TwitchUser, Depends(get_authenticated_twitch_user)],
) -> Response:
    return template.TemplateResponse(request=request, name="bot_dashboard.html", context={"user": current_twitch_user})
