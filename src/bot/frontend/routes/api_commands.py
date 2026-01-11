from http import HTTPStatus
from typing import Final

from fastapi import APIRouter
from fastapi import Depends
from starlette.requests import Request
from starlette.responses import JSONResponse

from bot.core.commands import delete_command as delete_command_core
from bot.core.commands import save_command as save_command_core
from bot.core.commands import update_command_message as update_command_message_core
from bot.core.commands import update_command_name as update_command_name_core
from bot.frontend.helpers.auth import get_authenticated_twitch_user
from bot.frontend.helpers.cast import to_int_or_raise

router: Final = APIRouter(prefix="/api/command", dependencies=[Depends(get_authenticated_twitch_user)])


@router.post("/create")
async def create_command(request: Request) -> JSONResponse:
    data = await request.json()
    id_ = to_int_or_raise(data.get("bot_id"))
    name = data.get("name")
    message = data.get("message")

    result = save_command_core(
        id_,
        name,
        message,
    )

    if not result.state.is_success():
        return JSONResponse(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR, content={"message": "Command could not be saved"}
        )

    return JSONResponse(status_code=HTTPStatus.OK, content={"message": "Command saved successfully"})


@router.post("/update/message")
async def update_command_message(request: Request) -> JSONResponse:
    data = await request.json()
    id_ = to_int_or_raise(data.get("bot_id"))
    name = data.get("name")
    message = data.get("message")

    result = update_command_message_core(id_, name, message)

    if not result.state.is_success():
        return JSONResponse(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR, content={"message": "Command could not be edited"}
        )

    return JSONResponse(status_code=HTTPStatus.OK, content={"message": "Command edited successfully"})


@router.post("/update/name")
async def update_command_name(request: Request) -> JSONResponse:
    data = await request.json()
    id_ = to_int_or_raise(data.get("bot_id").strip())
    old_name = data.get("old_name").strip()
    new_name = data.get("new_name").strip()

    result = update_command_name_core(id_, old_name, new_name)

    if not result.state.is_success():
        return JSONResponse(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR, content={"message": "Command could not be renamed"}
        )

    return JSONResponse(status_code=HTTPStatus.OK, content={"message": "Command renamed successfully"})


@router.post("/remove")
async def remove_command(request: Request) -> JSONResponse:
    data = await request.json()
    id_ = to_int_or_raise(data.get("bot_id"))
    name = data.get("name")

    result = delete_command_core(id_, name)

    if not result.state.is_success():
        return JSONResponse(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR, content={"message": "Command could not be removed"}
        )

    return JSONResponse(status_code=HTTPStatus.OK, content={"message": "Command removed successfully"})
