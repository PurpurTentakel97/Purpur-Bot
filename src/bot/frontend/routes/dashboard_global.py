from http import HTTPStatus
from typing import Annotated
from typing import Final
from typing import Optional

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Form
from fastapi.responses import RedirectResponse
from starlette.requests import Request
from starlette.responses import Response
from starlette.templating import Jinja2Templates

from bot.core.bot import update_bot as update_bot_core
from bot.core.bot import update_bot_enabled_by_id as update_bot_enabled_by_id_core
from bot.database.types.bot_config import BotConfigDB
from bot.frontend.helpers.auth import get_authenticated_twitch_user
from bot.frontend.helpers.auth import get_discord_user
from bot.frontend.helpers.decorators import bot_owner_required
from bot.frontend.helpers.route_utils import get_templates
from bot.frontend.helpers.route_utils import get_valid_bot
from bot.frontend.types.discord_user_info import DiscordUserInfo
from bot.frontend.types.twitch_user_info import TwitchUserInfo

router: Final = APIRouter(prefix="/dashboard/global", dependencies=[Depends(get_authenticated_twitch_user)])


@router.get("/{bot_id:int}")
@bot_owner_required()
async def dashboard_main(
    request: Request,
    bot: Annotated[BotConfigDB, Depends(get_valid_bot)],
    twitch_user: Annotated[TwitchUserInfo, Depends(get_authenticated_twitch_user)],
    discord_user: Annotated[Optional[DiscordUserInfo], Depends(get_discord_user)],
    template: Annotated[Jinja2Templates, Depends(get_templates)],
) -> Response:
    return template.TemplateResponse(
        request=request,
        name="dashboard_global.html",
        context={
            "bot": bot,
            "twitch_user": twitch_user,
            "discord_user": discord_user,
        },
    )


@router.post("/{bot_id:int}")
@bot_owner_required()
async def dashboard_main_edit(
    bot: Annotated[BotConfigDB, Depends(get_valid_bot)],
    name: Annotated[str, Form()],
    enabled: Annotated[bool, Form()] = False,
) -> RedirectResponse:
    result = update_bot_core(bot_id=bot.id, name=name)
    if result.state.fail:
        return RedirectResponse(
            f"/dashboard/global/{bot.id}?error_message=Failed to update bot | reason: {result.state.name}",
            status_code=HTTPStatus.SEE_OTHER,
        )

    result_enabled = await update_bot_enabled_by_id_core(bot_id=bot.id, enabled=enabled)
    if result_enabled.state.fail:
        return RedirectResponse(
            f"/dashboard/global/{bot.id}?error_message=Failed to update bot enabled state "
            + "| reason: {result_enabled.state.name}",
            status_code=HTTPStatus.SEE_OTHER,
        )

    return RedirectResponse(
        f"/dashboard/global/{bot.id}?success_message=Bot updated successfully", status_code=HTTPStatus.SEE_OTHER
    )
