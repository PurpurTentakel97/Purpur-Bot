from http import HTTPStatus
from typing import Annotated
from typing import Final
from typing import Optional

from fastapi import APIRouter
from fastapi import Depends
from fastapi.responses import RedirectResponse
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import Response
from starlette.templating import Jinja2Templates

from bot.core.bot import add_bot as add_bot_core
from bot.core.bot import delete_bot as delete_bot_core
from bot.core.bot import get_bots_by_twitch_id as get_bots_by_twitch_id_core
from bot.core.types.result import Result
from bot.core.types.result import ResultState
from bot.frontend.helpers.auth import get_authenticated_twitch_user
from bot.frontend.helpers.auth import get_discord_user
from bot.frontend.helpers.auth import get_twitch_user
from bot.frontend.helpers.route_utils import get_templates
from bot.frontend.types.discord_user_info import DiscordUserInfo
from bot.frontend.types.twitch_user_info import TwitchUserInfo

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

    bots = get_bots_by_twitch_id_core(twitch_user.id_) if twitch_user else Result(ResultState.NO_DATA, [])

    if bots.value is None:
        raise HTTPException(status_code=404, detail="Bots not found")

    return template.TemplateResponse(
        request=request,
        name="home.html",
        context={"twitch_user": twitch_user, "discord_user": discord_user, "bots": bots.value},
    )


@router.post("/bot")
async def bot_create(
    twitch_user: Annotated[TwitchUserInfo, Depends(get_authenticated_twitch_user)],
) -> RedirectResponse:
    result = add_bot_core(twitch_user.id_)
    if result.value is None:
        return RedirectResponse(
            url=f"/?error_message=Failed to create a bot | reason: {result.state.name}",
            status_code=HTTPStatus.SEE_OTHER,
        )

    return RedirectResponse(url="/?success_message=new bot added", status_code=HTTPStatus.SEE_OTHER)


@router.post("/bot/delete/{bot_id:int}")
async def bot_delete(
    twitch_user: Annotated[TwitchUserInfo, Depends(get_authenticated_twitch_user)],  # twitch user for authentication
    bot_id: int,
) -> RedirectResponse:
    result = await delete_bot_core(bot_id)

    if result.state.fail:
        return RedirectResponse(
            url=f"/?error_message=Failed to delete a bot | reason: {result.state.name}",
            status_code=HTTPStatus.SEE_OTHER,
        )

    return RedirectResponse(url="/?success_message=Bot deleted successfully", status_code=HTTPStatus.SEE_OTHER)
