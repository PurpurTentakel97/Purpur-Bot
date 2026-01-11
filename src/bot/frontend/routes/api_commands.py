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
    try:
        data = await request.json()
        bot_id = to_int_or_raise(data.get("bot_id"))
        name = data.get("name")
        message = data.get("message")

        result = save_command_core(
            bot_id,
            name,
            message,
        )

        if result.state.fail:
            return JSONResponse(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                content={"message": f"Command could not be saved | reason: {result.state.name}"},
            )

        return JSONResponse(status_code=HTTPStatus.OK, content={"message": "Command saved successfully"})

    except Exception as e:
        return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"message": str(e)})


@router.post("/update/message")
async def update_command_message(request: Request) -> JSONResponse:
    try:
        data = await request.json()
        id_ = to_int_or_raise(data.get("bot_id"))
        name = data.get("name")
        message = data.get("message")

        result = update_command_message_core(id_, name, message)

        if result.state.fail:
            return JSONResponse(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                content={"message": f"Command could not be edited | reason: {result.state.name}"},
            )

        return JSONResponse(status_code=HTTPStatus.OK, content={"message": "Command edited successfully"})

    except Exception as e:
        return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"message": str(e)})


@router.post("/update/name")
async def update_command_name(request: Request) -> JSONResponse:
    try:
        data = await request.json()
        id_ = to_int_or_raise(data.get("bot_id").strip())
        old_name = data.get("old_name").strip()
        new_name = data.get("new_name").strip()

        result = update_command_name_core(id_, old_name, new_name)

        if result.state.fail:
            return JSONResponse(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                content={"message": f"Command could not be renamed | reason: {result.state.name}"},
            )

        return JSONResponse(status_code=HTTPStatus.OK, content={"message": "Command renamed successfully"})

    except Exception as e:
        return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"message": str(e)})


@router.post("/remove")
async def remove_command(request: Request) -> JSONResponse:
    try:
        data = await request.json()
        id_ = to_int_or_raise(data.get("bot_id"))
        name = data.get("name")

        result = delete_command_core(id_, name)

        if result.state.fail:
            return JSONResponse(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                content={"message": f"Command could not be removed | reason: {result.state.name}"},
            )

        return JSONResponse(status_code=HTTPStatus.OK, content={"message": "Command removed successfully"})

    except Exception as e:
        return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"message": str(e)})
