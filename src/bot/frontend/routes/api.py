from http import HTTPStatus
from typing import Annotated
from typing import Final

from fastapi import APIRouter
from fastapi import Depends
from fastapi.responses import JSONResponse
from starlette.requests import Request

from bot.database.bot import add_twitch_channel_to_bot
from bot.database.bot import create_new_bot
from bot.database.bot import delete_bot_by_id
from bot.database.bot import delete_twitch_channel_from_bot
from bot.database.bot import get_bot_by_id
from bot.database.bot import update_bot
from bot.frontend.helpers.auth import get_authenticated_twitch_user
from bot.frontend.helpers.route_utils import get_twitch_session_cookie
from bot.types.twitch_user_info import TwitchUserInfo

router: Final = APIRouter(prefix="/api", dependencies=[Depends(get_authenticated_twitch_user)])


# bot
@router.post("/bot/create")
def new_bot(
    request: Request, current_twitch_user: Annotated[TwitchUserInfo, Depends(get_authenticated_twitch_user)]
) -> JSONResponse:
    result = create_new_bot(current_twitch_user.id_)
    if result is None:
        return JSONResponse(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, content={"message": "Failed to create a bot"})
    return JSONResponse(status_code=HTTPStatus.CREATED, content={"id": result})


@router.post("/bot/edit/{bot_id:int}")
async def edit_bot(
    request: Request,
    bot_id: int,
    current_twitch_user: Annotated[TwitchUserInfo, Depends(get_authenticated_twitch_user)],
) -> JSONResponse:
    try:
        data = await request.json()
        new_name = data.get("name")
        if not new_name:
            return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"message": "Bot name is required"})

        result = update_bot(bot_id, current_twitch_user.id_, new_name)

        if not result:
            return JSONResponse(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR, content={"message": "Failed to update bot"}
            )

        return JSONResponse(status_code=HTTPStatus.OK, content={"message": "Bot updated successfully"})

    except Exception as e:
        return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"message": str(e)})


@router.post("/bot/delete/{bot_id:int}")
def delete_bot(
    request: Request,
    bot_id: int,
    current_twitch_user: Annotated[TwitchUserInfo, Depends(get_authenticated_twitch_user)],
) -> JSONResponse:
    session_cookie = get_twitch_session_cookie(request)
    if session_cookie is None:
        return JSONResponse(status_code=HTTPStatus.UNAUTHORIZED, content={"message": "Session cookie is missing"})

    result = delete_bot_by_id(bot_id, current_twitch_user.id_)

    if not result:
        return JSONResponse(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, content={"message": "Failed to delete a bot"})
    return JSONResponse(status_code=HTTPStatus.OK, content={"message": "Bot deleted successfully"})


# Twitch
@router.post("/bot/twitch/add")
async def add_twitch_channel(
    request: Request, current_twitch_user: Annotated[TwitchUserInfo, Depends(get_authenticated_twitch_user)]
) -> JSONResponse:
    data = await request.json()
    bot_id = data.get("bot_id")
    twitch_channel = data.get("twitch_channel")

    bot = get_bot_by_id(bot_id)
    if bot is None or bot.twitch_user_id != current_twitch_user.id_:
        return JSONResponse(status_code=HTTPStatus.FORBIDDEN, content={"message": "Forbidden"})

    result = await add_twitch_channel_to_bot(bot_id, twitch_channel)

    if not result:
        return JSONResponse(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR, content={"message": "Failed to add a twitch channel to bot"}
        )
    return JSONResponse(status_code=HTTPStatus.OK, content={"message": "Twitch channel added successfully"})


@router.post("/bot/twitch/delete")
async def delete_twitch_channel(
    request: Request, current_twitch_user: Annotated[TwitchUserInfo, Depends(get_authenticated_twitch_user)]
) -> JSONResponse:
    data = await request.json()
    bot_id = data.get("bot_id")
    twitch_channel = data.get("twitch_channel")

    bot = get_bot_by_id(bot_id)
    if bot is None or bot.twitch_user_id != current_twitch_user.id_:
        return JSONResponse(status_code=HTTPStatus.FORBIDDEN, content={"message": "Forbidden"})

    result = await delete_twitch_channel_from_bot(bot_id, twitch_channel)

    if not result:
        return JSONResponse(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR, content={"message": "Failed to delete twitch channel"}
        )
    return JSONResponse(status_code=HTTPStatus.OK, content={"message": "Twitch channel deleted successfully"})
