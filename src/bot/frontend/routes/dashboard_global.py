from http import HTTPStatus
from typing import Annotated
from typing import Optional

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Form
from fastapi.responses import RedirectResponse
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import Response
from starlette.templating import Jinja2Templates

from bot.core.bot import get_bot as get_bot_core
from bot.core.bot import update_bot as update_bot_core
from bot.frontend.helpers.auth import get_authenticated_twitch_user
from bot.frontend.helpers.auth import get_discord_user
from bot.frontend.helpers.route_utils import get_templates
from bot.frontend.types.discord_user_info import DiscordUserInfo
from bot.frontend.types.twitch_user_info import TwitchUserInfo

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


@router.post("/{bot_id:int}")
async def dashboard_main_edit(
    request: Request,
    bot_id: int,
    name: Annotated[str, Form()],
) -> RedirectResponse:
    bot = get_bot_core(bot_id)
    if bot.value is None:
        raise HTTPException(status_code=404, detail="Bot not found")

    result = update_bot_core(bot_id=bot_id, name=name)
    if result.state.fail:
        return RedirectResponse(
            f"/dashboard/global/{bot_id}?error_message=Failed to update bot | reason: {result.state.name}",
            status_code=HTTPStatus.SEE_OTHER,
        )

    return RedirectResponse(
        f"/dashboard/global/{bot_id}?success_message=Bot updated successfully", status_code=HTTPStatus.SEE_OTHER
    )
