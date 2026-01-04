from http import HTTPStatus
from typing import Annotated
from typing import Final

from fastapi import APIRouter
from fastapi import Depends
from starlette.requests import Request
from starlette.responses import JSONResponse

from bot.database.bot import get_bot_by_id
from bot.database.commands import delete_command
from bot.database.commands import edit_command_message
from bot.database.commands import edit_command_name
from bot.database.commands import save_command
from bot.frontend.helpers.auth import get_authenticated_twitch_user
from bot.types.twitch_user_info import TwitchUserInfo

router: Final = APIRouter(prefix="/api/command", dependencies=[Depends(get_authenticated_twitch_user)])


@router.post("/create")
async def create_command(
    request: Request, current_twitch_user: Annotated[TwitchUserInfo, Depends(get_authenticated_twitch_user)]
) -> JSONResponse:
    data = await request.json()
    id_ = data.get("bot_id").strip()
    name = data.get("command_name").strip()
    message = data.get("command_message").strip()

    if any(char.isspace() for char in name):
        return JSONResponse(
            status_code=HTTPStatus.BAD_REQUEST, content={"message": "Command name cannot contain spaces"}
        )

    bot = get_bot_by_id(id_)
    if bot is None or bot.twitch_user_id != current_twitch_user.id_:
        return JSONResponse(status_code=HTTPStatus.FORBIDDEN, content={"message": "Forbidden"})

    result = save_command(
        bot_id=id_,
        command_name=name,
        command_message=message,
    )

    if not result:
        return JSONResponse(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR, content={"message": "Command could not be saved"}
        )

    return JSONResponse(status_code=HTTPStatus.OK, content={"message": "Command saved successfully"})


@router.post("/update/message")
async def update_command_message(
    request: Request, current_twitch_user: Annotated[TwitchUserInfo, Depends(get_authenticated_twitch_user)]
) -> JSONResponse:
    data = await request.json()
    id_ = data.get("bot_id").strip()
    name = data.get("command_name").strip()
    message = data.get("command_message").strip()

    bot = get_bot_by_id(id_)
    if bot is None or bot.twitch_user_id != current_twitch_user.id_:
        return JSONResponse(status_code=HTTPStatus.FORBIDDEN, content={"message": "Forbidden"})

    result = edit_command_message(bot_id=id_, command_name=name, command_message=message)

    if not result:
        return JSONResponse(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR, content={"message": "Command could not be edited"}
        )

    return JSONResponse(status_code=HTTPStatus.OK, content={"message": "Command edited successfully"})


@router.post("/update/name")
async def update_command_name(
    request: Request, current_twitch_user: Annotated[TwitchUserInfo, Depends(get_authenticated_twitch_user)]
) -> JSONResponse:
    data = await request.json()
    id_ = data.get("bot_id").strip()
    old_name = data.get("old_command_name").strip()
    new_name = data.get("new_command_name").strip()

    if any(char.isspace() for char in new_name):
        return JSONResponse(
            status_code=HTTPStatus.BAD_REQUEST, content={"message": "Command name cannot contain spaces"}
        )

    bot = get_bot_by_id(id_)
    if bot is None or bot.twitch_user_id != current_twitch_user.id_:
        return JSONResponse(status_code=HTTPStatus.FORBIDDEN, content={"message": "Forbidden"})

    result = edit_command_name(bot_id=id_, old_command_name=old_name, new_command_name=new_name)

    if not result:
        return JSONResponse(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR, content={"message": "Command could not be renamed"}
        )

    return JSONResponse(status_code=HTTPStatus.OK, content={"message": "Command renamed successfully"})


@router.post("/remove")
async def remove_command(
    request: Request, current_twitch_user: Annotated[TwitchUserInfo, Depends(get_authenticated_twitch_user)]
) -> JSONResponse:
    data = await request.json()
    id_ = data.get("bot_id").strip()
    name = data.get("command_name").strip()

    bot = get_bot_by_id(id_)
    if bot is None or bot.twitch_user_id != current_twitch_user.id_:
        return JSONResponse(status_code=HTTPStatus.FORBIDDEN, content={"message": "Forbidden"})

    result = delete_command(bot_id=id_, command_name=name)

    if not result:
        return JSONResponse(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR, content={"message": "Command could not be removed"}
        )

    return JSONResponse(status_code=HTTPStatus.OK, content={"message": "Command removed successfully"})
