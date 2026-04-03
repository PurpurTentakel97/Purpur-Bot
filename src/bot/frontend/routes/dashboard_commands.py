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
from bot.core.commands import get_commands_by_bot_id as get_commands_by_bot_id_core
from bot.core.commands import save_command as save_command_core
from bot.core.commands import update_command_by_id as update_command_by_id_core
from bot.database.types.base_command import BasicCommandDB
from bot.database.types.bot_config import BotConfigDB
from bot.frontend.helpers.decorators import get_optional_owned_discord_user
from bot.frontend.helpers.decorators import get_owned_bot
from bot.frontend.helpers.decorators import get_owned_command
from bot.frontend.helpers.decorators import get_owned_twitch_user
from bot.frontend.helpers.route_utils import get_templates
from bot.frontend.types.discord_user_info import DiscordUserInfo
from bot.frontend.types.twitch_user_info import TwitchUserInfo

router = APIRouter(prefix="/dashboard/commands/{bot_id:int}", dependencies=[Depends(get_owned_twitch_user)])


@router.get("")
async def dashboard_commands(
    request: Request,
    bot: Annotated[BotConfigDB, Depends(get_owned_bot)],
    template: Annotated[Jinja2Templates, Depends(get_templates)],
    twitch_user: Annotated[TwitchUserInfo, Depends(get_owned_twitch_user)],
    discord_user: Annotated[Optional[DiscordUserInfo], Depends(get_optional_owned_discord_user)],
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


@router.post("")
async def dashboard_command_add(
    bot: Annotated[BotConfigDB, Depends(get_owned_bot)],
    name: Annotated[str, Form()],
    message: Annotated[str, Form()],
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


@router.post("/update/{command_id:int}")
async def dashboard_command_update(
    command: Annotated[BasicCommandDB, Depends(get_owned_command)],
    name: Annotated[str, Form()],
    message: Annotated[str, Form()],
    enabled: Annotated[bool, Form()] = False,
) -> RedirectResponse:
    result = update_command_by_id_core(command.bot_id, command.id, name, message, enabled)

    if result.state.fail:
        return RedirectResponse(
            url=f"/dashboard/commands/{command.bot_id}?error_message=Failed to update command name "
            + f"| reason: {result.state.name}",
            status_code=HTTPStatus.SEE_OTHER,
        )

    return RedirectResponse(
        url=f"/dashboard/commands/{command.bot_id}?success_message=Command name updated successfully",
        status_code=HTTPStatus.SEE_OTHER,
    )


@router.post("/delete/{command_id:int}")
async def dashboard_command_delete(
    command: Annotated[BasicCommandDB, Depends(get_owned_command)],
) -> RedirectResponse:
    result = delete_command_by_id_core(command.id)

    if result.state.fail:
        return RedirectResponse(
            url=f"/dashboard/commands/{command.bot_id}?error_message=Failed to delete command "
            + f"| reason: {result.state.name}",
            status_code=HTTPStatus.SEE_OTHER,
        )
    return RedirectResponse(
        url=f"/dashboard/commands/{command.bot_id}?success_message=Command deleted successfully",
        status_code=HTTPStatus.SEE_OTHER,
    )
