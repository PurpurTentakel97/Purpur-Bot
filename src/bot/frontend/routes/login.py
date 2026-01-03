from typing import Annotated
from typing import Final
from typing import Optional

from fastapi import APIRouter
from fastapi import Depends
from starlette.requests import Request
from starlette.responses import Response
from starlette.templating import Jinja2Templates

from bot.frontend.helpers.auth import get_twitch_user
from bot.frontend.helpers.route_utils import get_templates
from bot.types.twitch_user_info import TwitchUserInfo

router: Final = APIRouter()


@router.get("/login")
async def login(
    request: Request,
    templates: Annotated[Jinja2Templates, Depends(get_templates)],
    user: Annotated[Optional[TwitchUserInfo], Depends(get_twitch_user)],
) -> Response:
    return templates.TemplateResponse(request=request, name="login.html", context={"user": user})
