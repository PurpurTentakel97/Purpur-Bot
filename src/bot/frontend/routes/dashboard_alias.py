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

from bot.core.alias_dict import add_alias as add_alias_core
from bot.core.alias_dict import delete_alias_by_id as delete_alias_by_id_core
from bot.core.alias_dict import get_alias_dict_from_bot as select_dict_from_bot_core
from bot.core.alias_dict import update_alias_by_id as update_alias_by_id_core
from bot.database.types.alias_dict_entry import AliasDictEntry
from bot.database.types.bot_config import BotConfigDB
from bot.frontend.helpers.decorators import get_optional_owned_discord_user
from bot.frontend.helpers.decorators import get_owned_alias
from bot.frontend.helpers.decorators import get_owned_bot
from bot.frontend.helpers.decorators import get_owned_twitch_user
from bot.frontend.helpers.route_utils import get_templates
from bot.frontend.types.discord_user_info import DiscordUserInfo
from bot.frontend.types.twitch_user_info import TwitchUserInfo

router = APIRouter(prefix="/dashboard/alias/{bot_id:int}", dependencies=[Depends(get_owned_twitch_user)])


@router.get("")
async def dashboard_alias(
    request: Request,
    bot: Annotated[BotConfigDB, Depends(get_owned_bot)],
    template: Annotated[Jinja2Templates, Depends(get_templates)],
    twitch_user: Annotated[TwitchUserInfo, Depends(get_owned_twitch_user)],
    discord_user: Annotated[Optional[DiscordUserInfo], Depends(get_optional_owned_discord_user)],
) -> Response:
    aliases = select_dict_from_bot_core(bot.id)
    if aliases.value is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Aliases not found")

    return template.TemplateResponse(
        request=request,
        name="dashboard_alias.html",
        context={
            "bot": bot,
            "twitch_user": twitch_user,
            "discord_user": discord_user,
            "aliases": aliases.value,
        },
    )


@router.post("")
async def dashboard_alias_add(
    bot: Annotated[BotConfigDB, Depends(get_owned_bot)],
    alias: Annotated[str, Form()],
    explanation: Annotated[str, Form()],
) -> RedirectResponse:
    result = add_alias_core(bot.id, alias, explanation)

    if result.state.fail:
        return RedirectResponse(
            url=f"/dashboard/alias/{bot.id}?error_message=Failed to save alias | reason: {result.state.name}",
            status_code=HTTPStatus.SEE_OTHER,
        )

    return RedirectResponse(
        url=f"/dashboard/alias/{bot.id}?success_message=Alias saved successfully", status_code=HTTPStatus.SEE_OTHER
    )


@router.post("/update/{alias_id:int}")
async def dashboard_alias_update(
    entry: Annotated[AliasDictEntry, Depends(get_owned_alias)],
    alias: Annotated[str, Form()],
    explanation: Annotated[str, Form()],
    enabled: Annotated[bool, Form()] = False,
) -> RedirectResponse:
    result = update_alias_by_id_core(entry.id, alias, explanation, enabled)

    if result.state.fail:
        return RedirectResponse(
            url=f"/dashboard/alias/{entry.bot_id}?error_message=Failed to update alias "
            + f"| reason: {result.state.name}",
            status_code=HTTPStatus.SEE_OTHER,
        )

    return RedirectResponse(
        url=f"/dashboard/alias/{entry.bot_id}?success_message=Alias updated successfully",
        status_code=HTTPStatus.SEE_OTHER,
    )


@router.post("/{alias_id:int}/delete")
async def dashboard_alias_delete(
    entry: Annotated[AliasDictEntry, Depends(get_owned_alias)],
) -> RedirectResponse:
    result = delete_alias_by_id_core(entry.id)

    if result.state.fail:
        return RedirectResponse(
            url=f"/dashboard/alias/{entry.bot_id}?error_message=Failed to delete alias "
            + f"| reason: {result.state.name}",
            status_code=HTTPStatus.SEE_OTHER,
        )

    return RedirectResponse(
        url=f"/dashboard/alias/{entry.bot_id}?success_message=Alias deleted successfully",
        status_code=HTTPStatus.SEE_OTHER,
    )
