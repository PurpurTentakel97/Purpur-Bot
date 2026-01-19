from http import HTTPStatus
from typing import Annotated
from typing import Optional

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Form
from fastapi.responses import RedirectResponse
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import Response
from starlette.templating import Jinja2Templates

from bot.core.commands import delete_command_by_id as delete_command_by_id_core
from bot.core.commands import get_command_by_id as get_command_by_id_core
from bot.core.commands import get_commands_by_bot_id as get_commands_by_bot_id_core
from bot.core.commands import save_command as save_command_core
from bot.core.commands import update_command_message_by_id as update_command_message_by_id_core
from bot.core.commands import update_command_name_by_id as update_command_name_by_id_core
from bot.core.types.result import Result
from bot.database.types.base_command import BasicCommandDB
from bot.database.types.bot_config import BotConfigDB
from bot.frontend.helpers.auth import get_authenticated_twitch_user
from bot.frontend.helpers.auth import get_discord_user
from bot.frontend.helpers.route_utils import get_templates
from bot.frontend.helpers.route_utils import get_valid_bot
from bot.frontend.types.discord_user_info import DiscordUserInfo
from bot.frontend.types.twitch_user_info import TwitchUserInfo

router = APIRouter(prefix="/dashboard/commands", dependencies=[Depends(get_authenticated_twitch_user)])


@router.get("/{bot_id:int}")
async def dashboard_commands(
    request: Request,
    bot: Annotated[BotConfigDB, Depends(get_valid_bot)],
    template: Annotated[Jinja2Templates, Depends(get_templates)],
    twitch_user: Annotated[TwitchUserInfo, Depends(get_authenticated_twitch_user)],
    discord_user: Annotated[Optional[DiscordUserInfo], Depends(get_discord_user)],
) -> Response:
    commands = get_commands_by_bot_id_core(bot.id)
    if commands.value is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Commands not found")

    return template.TemplateResponse(
        request=request,
        name="dashboard_commands.html",
        context={
            "bot": bot,
            "twitch_user": twitch_user,
            "discord_user": discord_user,
            "commands": commands.value,
        },
    )


@router.post("/{bot_id:int}")
async def dashboard_command_add(
    bot: Annotated[BotConfigDB, Depends(get_valid_bot)], name: Annotated[str, Form()], message: Annotated[str, Form()]
) -> RedirectResponse:
    result = save_command_core(bot.id, name, message)

    if result.state.fail:
        return RedirectResponse(
            url=f"/dashboard/commands/{bot.id}?error_message=Failed to save command | reason: {result.state.name}",
            status_code=HTTPStatus.SEE_OTHER,
        )

    return RedirectResponse(
        url=f"/dashboard/commands/{bot.id}?success_message=Command saved successfully", status_code=HTTPStatus.SEE_OTHER
    )


@router.post("/{command_id:int}/name")
async def dashboard_command_update_name(
    command: Annotated[Result[BasicCommandDB], Depends(get_command_by_id_core)], name: Annotated[str, Form()]
) -> RedirectResponse:
    if command.value is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Command not found")

    result = update_command_name_by_id_core(command.value.id, name)

    if result.state.fail:
        return RedirectResponse(
            url=f"/dashboard/commands/{command.value.bot_id}?error_message=Failed to update command name "
            + f"| reason: {result.state.name}",
            status_code=HTTPStatus.SEE_OTHER,
        )

    return RedirectResponse(
        url=f"/dashboard/commands/{command.value.bot_id}?success_message=Command name updated successfully",
        status_code=HTTPStatus.SEE_OTHER,
    )


@router.post("/{command_id:int}/message")
async def dashboard_command_update_message(
    command: Annotated[Result[BasicCommandDB], Depends(get_command_by_id_core)], message: Annotated[str, Form()]
) -> RedirectResponse:
    if command.value is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Command not found")

    result = update_command_message_by_id_core(command.value.id, message)

    if result.state.fail:
        return RedirectResponse(
            url=f"/dashboard/commands/{command.value.bot_id}?error_message=Failed to update command message "
            + f"| reason: {result.state.name}",
            status_code=HTTPStatus.SEE_OTHER,
        )

    return RedirectResponse(
        url=f"/dashboard/commands/{command.value.bot_id}?success_message=Command message updated successfully",
        status_code=HTTPStatus.SEE_OTHER,
    )


@router.post("/{command_id:int}/delete")
async def dashboard_command_delete(
    command: Annotated[Result[BasicCommandDB], Depends(get_command_by_id_core)],
) -> RedirectResponse:
    if command.value is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Command not found")

    result = delete_command_by_id_core(command.value.id)

    if result.state.fail:
        return RedirectResponse(
            url=f"/dashboard/commands/{command.value.bot_id}?error_message=Failed to delete command "
            + f"| reason: {result.state.name}",
            status_code=HTTPStatus.SEE_OTHER,
        )
    return RedirectResponse(
        url=f"/dashboard/commands/{command.value.bot_id}?success_message=Command deleted successfully",
        status_code=HTTPStatus.SEE_OTHER,
    )
