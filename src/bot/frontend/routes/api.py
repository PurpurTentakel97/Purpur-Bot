from http import HTTPStatus
from typing import Annotated
from typing import Final

from fastapi import APIRouter
from fastapi import Depends
from starlette.requests import Request
from starlette.responses import Response

from bot.database.bot import create_new_bot
from bot.frontend.helpers.auth import get_authenticated_twitch_user
from bot.types.twitch_user_info import TwitchUserInfo

router: Final = APIRouter(prefix="/api", dependencies=[Depends(get_authenticated_twitch_user)])


@router.post("/bot/create")
def new_bot(
    request: Request, current_twitch_user: Annotated[TwitchUserInfo, Depends(get_authenticated_twitch_user)]
) -> Response:
    result = create_new_bot(current_twitch_user.id_)
    if result is None:
        return Response(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, content="Failed to create a bot")
    return Response(status_code=HTTPStatus.CREATED, content=f"Bot created successfully, ID: {result}")
