from typing import Annotated
from typing import Final

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from starlette.requests import Request
from starlette.responses import Response
from starlette.templating import Jinja2Templates

from bot.database.bot import get_bot_by_id
from bot.database.bot import get_twitch_channels_by_bot_id
from bot.frontend.helpers.auth import get_authenticated_twitch_user
from bot.frontend.helpers.route_utils import get_templates
from bot.frontend.helpers.twitch import get_allowed_twitch_channels
from bot.types.twitch_user_info import TwitchUserInfo

router: Final = APIRouter(prefix="/dashboard", dependencies=[Depends(get_authenticated_twitch_user)])


@router.get("/bot/edit/{bot_id:int}")
async def bot_dashboard(
    request: Request,
    bot_id: int,
    template: Annotated[Jinja2Templates, Depends(get_templates)],
    current_twitch_user: Annotated[TwitchUserInfo, Depends(get_authenticated_twitch_user)],
) -> Response:
    bot = get_bot_by_id(bot_id)
    if bot is None:
        raise HTTPException(status_code=404, detail="Bot not found")

    if bot.twitch_user_id != current_twitch_user.id_:
        raise HTTPException(status_code=403, detail="You do not have permission to edit this bot")

    twitch_channels = get_twitch_channels_by_bot_id(bot_id)
    allowed_channels = await get_allowed_twitch_channels(current_twitch_user.id_, current_twitch_user.login)

    # filter allowed_channels to only include those that are not yet in twitch_channels
    joined_channel_names = {c.channel_name.lower() for c in twitch_channels}
    filtered_allowed_channels = [c for c in allowed_channels if c.lower() not in joined_channel_names]

    return template.TemplateResponse(
        request=request,
        name="bot_dashboard.html",
        context={
            "bot": bot,
            "twitch_channels": twitch_channels,
            "allowed_channels": filtered_allowed_channels,
        },
    )
