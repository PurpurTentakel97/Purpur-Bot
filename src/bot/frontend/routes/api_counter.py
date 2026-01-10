from http import HTTPStatus
from typing import Final

from fastapi import APIRouter
from fastapi import Depends
from starlette.requests import Request
from starlette.responses import JSONResponse

from bot.frontend.helpers.auth import get_authenticated_twitch_user
from bot.frontend.helpers.cast import to_int_or_raise
from bot.core.counter import save_counter as save_counter_core
from bot.core.counter import edit_counter_name as edit_counter_name_core
from bot.core.counter import edit_counter_value as edit_counter_value_core
from bot.core.counter import reset_counter as reset_counter_core
from bot.core.counter import delete_counter as delete_counter_core

router: Final = APIRouter(prefix="/api/counter", dependencies=[Depends(get_authenticated_twitch_user)])


@router.post("/create")
async def create_counter(request: Request) -> JSONResponse:
    data = await request.json()
    bot_id = to_int_or_raise(data.get("bot_id"))
    name = data.get("name")

    result = save_counter_core(bot_id, name)

    if not result:
        return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"message": "Failed to create counter"})
    return JSONResponse(status_code=HTTPStatus.OK, content={"message": "Counter created successfully"})


@router.post("/reset")
async def reset_counter(request: Request) -> JSONResponse:
    data = await request.json()
    name = data.get("name")
    bot_id = to_int_or_raise(data.get("bot_id"))

    result = reset_counter_core(bot_id, name)

    if not result:
        return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"message": "Failed to reset counter"})
    return JSONResponse(status_code=HTTPStatus.OK, content={"message": "Counter reset successfully"})


@router.post("/delete")
async def delete_counter(request: Request) -> JSONResponse:
    data = await request.json()
    name = data.get("name")
    bot_id = to_int_or_raise(data.get("bot_id"))

    result = delete_counter_core(bot_id, name)

    if not result:
        return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"message": "Failed to delete counter"})
    return JSONResponse(status_code=HTTPStatus.OK, content={"message": "Counter deleted successfully"})


@router.post("/update/name")
async def update_counter_name(request: Request) -> JSONResponse:
    data = await request.json()
    bot_id = to_int_or_raise(data.get("bot_id"))
    old_name = data.get("old_name")
    new_name = data.get("new_name")

    result = edit_counter_name_core(bot_id, old_name, new_name)

    if not result:
        return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"message": "Failed to rename counter"})
    return JSONResponse(status_code=HTTPStatus.OK, content={"message": "Counter renamed successfully"})


@router.post("/update/value")
async def update_counter_value(request: Request) -> JSONResponse:
    data = await request.json()
    bot_id = to_int_or_raise(data.get("bot_id"))
    name = data.get("name")
    value = to_int_or_raise(data.get("count"))

    result = edit_counter_value_core(bot_id, name, value)

    if not result:
        return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"message": "Failed to update counter count"})
    return JSONResponse(status_code=HTTPStatus.OK, content={"message": "Counter count updated successfully"})
