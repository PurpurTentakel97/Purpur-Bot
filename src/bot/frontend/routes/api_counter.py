from http import HTTPStatus
from typing import Annotated
from typing import Final

from fastapi import APIRouter
from fastapi import Depends
from starlette.requests import Request
from starlette.responses import JSONResponse

from bot.database.bot import get_bot_by_id
from bot.database.counter import delete_counter as delete_counter_db
from bot.database.counter import edit_counter_name as edit_counter_name_db
from bot.database.counter import edit_counter_value as edit_counter_value_db
from bot.database.counter import reset_counter as reset_counter_db
from bot.database.counter import save_counter as save_counter_db
from bot.frontend.helpers.auth import get_authenticated_twitch_user
from bot.types.frontend.twitch_user_info import TwitchUserInfo

router: Final = APIRouter(prefix="/api/counter", dependencies=[Depends(get_authenticated_twitch_user)])


@router.post("/create")
async def create_counter(
    request: Request, current_twitch_user: Annotated[TwitchUserInfo, Depends(get_authenticated_twitch_user)]
) -> JSONResponse:
    data = await request.json()
    name = data.get("name")
    bot_id = int(data.get("bot_id"))

    bot = get_bot_by_id(bot_id)
    if bot is None or bot.twitch_user_id != current_twitch_user.id_:
        return JSONResponse(status_code=HTTPStatus.FORBIDDEN, content={"message": "Forbidden"})

    result = save_counter_db(bot_id, name)

    if not result:
        return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"message": "Failed to create counter"})
    return JSONResponse(status_code=HTTPStatus.OK, content={"message": "Counter created successfully"})


@router.post("/reset")
async def reset_counter(
    request: Request, current_twitch_user: Annotated[TwitchUserInfo, Depends(get_authenticated_twitch_user)]
) -> JSONResponse:
    data = await request.json()
    name = data.get("name")
    bot_id = int(data.get("bot_id"))

    bot = get_bot_by_id(bot_id)
    if bot is None or bot.twitch_user_id != current_twitch_user.id_:
        return JSONResponse(status_code=HTTPStatus.FORBIDDEN, content={"message": "Forbidden"})

    result = reset_counter_db(bot_id, name)

    if not result:
        return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"message": "Failed to reset counter"})
    return JSONResponse(status_code=HTTPStatus.OK, content={"message": "Counter reset successfully"})


@router.post("/delete")
async def delete_counter(
    request: Request, current_twitch_user: Annotated[TwitchUserInfo, Depends(get_authenticated_twitch_user)]
) -> JSONResponse:
    data = await request.json()
    name = data.get("name")
    bot_id = int(data.get("bot_id"))

    bot = get_bot_by_id(bot_id)
    if bot is None or bot.twitch_user_id != current_twitch_user.id_:
        return JSONResponse(status_code=HTTPStatus.FORBIDDEN, content={"message": "Forbidden"})

    result = delete_counter_db(bot_id, name)

    if not result:
        return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"message": "Failed to delete counter"})
    return JSONResponse(status_code=HTTPStatus.OK, content={"message": "Counter deleted successfully"})


@router.post("/update/name")
async def update_counter_name(
    request: Request, current_twitch_user: Annotated[TwitchUserInfo, Depends(get_authenticated_twitch_user)]
) -> JSONResponse:
    data = await request.json()
    bot_id = int(data.get("bot_id"))
    old_name = data.get("old_name")
    new_name = data.get("new_name")

    bot = get_bot_by_id(bot_id)
    if bot is None or bot.twitch_user_id != current_twitch_user.id_:
        return JSONResponse(status_code=HTTPStatus.FORBIDDEN, content={"message": "Forbidden"})

    result = edit_counter_name_db(bot_id, old_name, new_name)

    if not result:
        return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"message": "Failed to rename counter"})
    return JSONResponse(status_code=HTTPStatus.OK, content={"message": "Counter renamed successfully"})


@router.post("/update/value")
async def update_counter_value(
    request: Request, current_twitch_user: Annotated[TwitchUserInfo, Depends(get_authenticated_twitch_user)]
) -> JSONResponse:
    data = await request.json()
    bot_id = int(data.get("bot_id"))
    name = data.get("name")
    value = int(data.get("count"))

    bot = get_bot_by_id(bot_id)
    if bot is None or bot.twitch_user_id != current_twitch_user.id_:
        return JSONResponse(status_code=HTTPStatus.FORBIDDEN, content={"message": "Forbidden"})

    result = edit_counter_value_db(bot_id, name, value)

    if not result:
        return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"message": "Failed to update counter count"})
    return JSONResponse(status_code=HTTPStatus.OK, content={"message": "Counter count updated successfully"})
