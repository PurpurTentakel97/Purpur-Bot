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

from bot.core.counter import delete_counter_by_id as delete_counter_by_id_core
from bot.core.counter import get_counter_by_id as get_counter_by_id_core
from bot.core.counter import get_counters_by_bot_id as get_counters_by_bot_id_core
from bot.core.counter import reset_counter_by_id as reset_counter_by_id_core
from bot.core.counter import save_counter as save_counter_core
from bot.core.counter import update_counter_by_id as update_counter_by_id_core
from bot.core.types.result import Result
from bot.database.types.bot_config import BotConfigDB
from bot.database.types.counter import CounterDB
from bot.frontend.helpers.auth import get_authenticated_twitch_user
from bot.frontend.helpers.auth import get_discord_user
from bot.frontend.helpers.decorators import ResourceType
from bot.frontend.helpers.decorators import bot_owner_required
from bot.frontend.helpers.decorators import resource_owner_required
from bot.frontend.helpers.route_utils import get_templates
from bot.frontend.helpers.route_utils import get_valid_bot
from bot.frontend.types.discord_user_info import DiscordUserInfo
from bot.frontend.types.twitch_user_info import TwitchUserInfo

router = APIRouter(prefix="/dashboard/counter", dependencies=[Depends(get_authenticated_twitch_user)])


@router.get("/{bot_id:int}")
@bot_owner_required()
async def dashboard_counter(
    request: Request,
    bot: Annotated[BotConfigDB, Depends(get_valid_bot)],
    template: Annotated[Jinja2Templates, Depends(get_templates)],
    twitch_user: Annotated[TwitchUserInfo, Depends(get_authenticated_twitch_user)],
    discord_user: Annotated[Optional[DiscordUserInfo], Depends(get_discord_user)],
) -> Response:
    counters = get_counters_by_bot_id_core(bot.id)
    if counters.value is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Counters not found")

    return template.TemplateResponse(
        request=request,
        name="dashboard_counter.html",
        context={
            "bot": bot,
            "twitch_user": twitch_user,
            "discord_user": discord_user,
            "counters": counters.value,
        },
    )


@router.post("/{bot_id:int}")
@bot_owner_required()
async def dashboard_counter_add(
    bot: Annotated[BotConfigDB, Depends(get_valid_bot)], name: Annotated[str, Form()]
) -> RedirectResponse:
    result = save_counter_core(bot.id, name)

    if result.state.fail:
        return RedirectResponse(
            url=f"/dashboard/counter/{bot.id}?error_message=Failed to save counter | reason: {result.state.name}",
            status_code=HTTPStatus.SEE_OTHER,
        )

    return RedirectResponse(
        url=f"/dashboard/counter/{bot.id}?success_message=Counter saved successfully", status_code=HTTPStatus.SEE_OTHER
    )


@router.post("/update/{resource_id:int}")
@resource_owner_required(ResourceType.COUNTER)
async def dashboard_counter_update(
    counter: Annotated[Result[CounterDB], Depends(get_counter_by_id_core)],
    name: Annotated[str, Form()],
    count: Annotated[int, Form()],
) -> RedirectResponse:
    if counter.value is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Counter not found")

    result = update_counter_by_id_core(counter.value.id, name, count)

    if result.state.fail:
        return RedirectResponse(
            url=f"/dashboard/counter/{counter.value.bot_id}?error_message=Failed to update counter "
            + f"| reason: {result.state.name}",
            status_code=HTTPStatus.SEE_OTHER,
        )

    return RedirectResponse(
        url=f"/dashboard/counter/{counter.value.bot_id}?success_message=Counter updated successfully",
        status_code=HTTPStatus.SEE_OTHER,
    )


@router.post("/{resource_id:int}/reset")
@resource_owner_required(ResourceType.COUNTER)
async def dashboard_counter_reset(
    counter: Annotated[Result[CounterDB], Depends(get_counter_by_id_core)],
) -> RedirectResponse:
    if counter.value is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Counter not found")

    result = reset_counter_by_id_core(counter.value.id)

    if result.state.fail:
        return RedirectResponse(
            url=f"/dashboard/counter/{counter.value.bot_id}?error_message=Failed to reset counter "
            + f"| reason: {result.state.name}",
            status_code=HTTPStatus.SEE_OTHER,
        )

    return RedirectResponse(
        url=f"/dashboard/counter/{counter.value.bot_id}?success_message=Counter reset successfully",
        status_code=HTTPStatus.SEE_OTHER,
    )


@router.post("/{resource_id:int}/delete")
@resource_owner_required(ResourceType.COUNTER)
async def dashboard_counter_delete(
    counter: Annotated[Result[CounterDB], Depends(get_counter_by_id_core)],
) -> RedirectResponse:
    if counter.value is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Counter not found")

    result = delete_counter_by_id_core(counter.value.id)

    if result.state.fail:
        return RedirectResponse(
            url=f"/dashboard/counter/{counter.value.bot_id}?error_message=Failed to delete counter "
            + f"| reason: {result.state.name}",
            status_code=HTTPStatus.SEE_OTHER,
        )

    return RedirectResponse(
        url=f"/dashboard/counter/{counter.value.bot_id}?success_message=Counter deleted successfully",
        status_code=HTTPStatus.SEE_OTHER,
    )
