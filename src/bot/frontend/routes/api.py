from http import HTTPStatus
from typing import Annotated
from typing import Final

from fastapi import APIRouter
from fastapi import Depends
from fastapi.responses import JSONResponse
from starlette.requests import Request

from bot.database.bot import create_new_bot
from bot.database.bot import delete_bot_by_id
from bot.frontend.helpers.auth import get_authenticated_twitch_user
from bot.frontend.helpers.route_utils import get_twitch_session_cookie
from bot.types.twitch_user_info import TwitchUserInfo

router: Final = APIRouter(prefix="/api", dependencies=[Depends(get_authenticated_twitch_user)])


@router.post("/bot/create")
def new_bot(
    request: Request, current_twitch_user: Annotated[TwitchUserInfo, Depends(get_authenticated_twitch_user)]
) -> JSONResponse:
    result = create_new_bot(current_twitch_user.id_)
    if result is None:
        return JSONResponse(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, content={"message": "Failed to create a bot"})
    return JSONResponse(status_code=HTTPStatus.CREATED, content={"id": result})


@router.post("/bot/delete/{bot_id:int}")
def delete_bot(
    request: Request,
    bot_id: int,
    current_twitch_user: Annotated[TwitchUserInfo, Depends(get_authenticated_twitch_user)],
) -> JSONResponse:
    session_cookie = get_twitch_session_cookie(request)
    if session_cookie is None:
        return JSONResponse(status_code=HTTPStatus.UNAUTHORIZED, content={"message": "Session cookie is missing"})

    if current_twitch_user.id_ != session_cookie.user_id:
        return JSONResponse(status_code=HTTPStatus.FORBIDDEN, content={"message": "You can only delete your own bots"})

    result = delete_bot_by_id(bot_id, current_twitch_user.id_)

    if not result:
        return JSONResponse(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, content={"message": "Failed to delete a bot"})
    return JSONResponse(status_code=HTTPStatus.OK, content={"message": "Bot deleted successfully"})
