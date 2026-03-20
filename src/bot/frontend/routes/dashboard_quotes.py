from http import HTTPStatus
from typing import Annotated
from typing import Final

from fastapi import APIRouter
from fastapi import Depends
from fastapi.responses import HTMLResponse
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from bot.core.quote import delete_quote_by_id
from bot.core.quote import edit_quote_by_id
from bot.core.quote import get_quotes_by_bot_id
from bot.database.types.bot_config import BotConfigDB
from bot.frontend.helpers.auth import get_authenticated_twitch_user
from bot.frontend.helpers.route_utils import get_templates
from bot.frontend.helpers.route_utils import get_valid_bot
from bot.frontend.types.twitch_user_info import TwitchUserInfo

router: Final = APIRouter(prefix="/dashboard/quotes", dependencies=[Depends(get_authenticated_twitch_user)])


@router.get("/{bot_id:int}")
async def dashboard_main(
    request: Request,
    bot: Annotated[BotConfigDB, Depends(get_valid_bot)],
    twitch_user: Annotated[TwitchUserInfo, Depends(get_authenticated_twitch_user)],
    template: Annotated[Jinja2Templates, Depends(get_templates)],
) -> HTMLResponse:
    quotes: Final = get_quotes_by_bot_id(bot.id)
    return template.TemplateResponse(
        request=request,
        name="dashboard/quotes.html",
        context={
            "bot": bot,
            "quotes": quotes,
            "twitch_user": twitch_user,
        },
    )


@router.post("/{bot_id:int}/edit/{quote_id:int}")
async def edit(
    request: Request,
    bot: Annotated[BotConfigDB, Depends(get_valid_bot)],
    quote_id: int,
    quote: str,
) -> RedirectResponse:
    result: Final = edit_quote_by_id(quote_id, quote)

    if result.state.fail:
        return RedirectResponse(
            url=f"/dashboard/quotes/{bot.id}?error_message=Failed to edit quote | reason: {result.state.name}",
            status_code=HTTPStatus.SEE_OTHER,
        )

    return RedirectResponse(
        url=f"/dashboard/quotes/{bot.id}?success_message=Quote edited successfully",
        status_code=HTTPStatus.SEE_OTHER,
    )


@router.post("/{bot_id:int}/delete/{quote_id:int}")
async def delete(
    request: Request, bot: Annotated[BotConfigDB, Depends(get_valid_bot)], quote_id: int
) -> RedirectResponse:
    result: Final = delete_quote_by_id(quote_id)

    if result.state.fail:
        return RedirectResponse(
            url=f"/dashboard/quotes/{bot.id}?error_message=Failed to delete quote | reason: {result.state.name}",
            status_code=HTTPStatus.SEE_OTHER,
        )

    return RedirectResponse(
        url=f"/dashboard/quotes/{bot.id}?success_message=Quote deleted successfully",
        status_code=HTTPStatus.SEE_OTHER,
    )
