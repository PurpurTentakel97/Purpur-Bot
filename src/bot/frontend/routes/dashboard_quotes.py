from http import HTTPStatus
from typing import Annotated
from typing import Final
from typing import Optional

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Form
from fastapi.responses import HTMLResponse
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from bot.core.quote import delete_quote_by_id
from bot.core.quote import edit_quote_by_id
from bot.core.quote import get_quotes_by_bot_id
from bot.database.types.bot_config import BotConfigDB
from bot.database.types.quote import Quote
from bot.frontend.helpers.decorators import get_optional_owned_discord_user
from bot.frontend.helpers.decorators import get_owned_bot
from bot.frontend.helpers.decorators import get_owned_quote
from bot.frontend.helpers.decorators import get_owned_twitch_user
from bot.frontend.helpers.route_utils import get_templates
from bot.frontend.types.discord_user_info import DiscordUserInfo
from bot.frontend.types.twitch_user_info import TwitchUserInfo

router: Final = APIRouter(prefix="/dashboard/quotes/{bot_id:int}", dependencies=[Depends(get_owned_twitch_user)])


@router.get("")
async def dashboard_main(
    request: Request,
    bot: Annotated[BotConfigDB, Depends(get_owned_bot)],
    twitch_user: Annotated[TwitchUserInfo, Depends(get_owned_twitch_user)],
    discord_user: Annotated[Optional[DiscordUserInfo], Depends(get_optional_owned_discord_user)],
    template: Annotated[Jinja2Templates, Depends(get_templates)],
) -> HTMLResponse:
    result: Final = await get_quotes_by_bot_id(bot.id)
    quotes = result.value if result.state.success and result.value is not None else []
    return template.TemplateResponse(
        request=request,
        name="dashboard_quotes.html",
        context={
            "bot": bot,
            "quotes": quotes,
            "twitch_user": twitch_user,
            "discord_user": discord_user,
        },
    )


@router.post("/edit/{quote_id:int}")
async def edit(
    bot: Annotated[BotConfigDB, Depends(get_owned_bot)],
    old_quote: Annotated[Quote, Depends(get_owned_quote)],
    quote: Annotated[str, Form()],
) -> RedirectResponse:
    result: Final = edit_quote_by_id(old_quote.id, quote)

    if result.state.fail:
        return RedirectResponse(
            url=f"/dashboard/quotes/{bot.id}?error_message=Failed to edit quote | reason: {result.state.name}",
            status_code=HTTPStatus.SEE_OTHER,
        )

    return RedirectResponse(
        url=f"/dashboard/quotes/{bot.id}?success_message=Quote edited successfully",
        status_code=HTTPStatus.SEE_OTHER,
    )


@router.post("/delete/{quote_id:int}")
async def delete(
    bot: Annotated[BotConfigDB, Depends(get_owned_bot)],
    quote: Annotated[Quote, Depends(get_owned_quote)],
) -> RedirectResponse:
    result: Final = delete_quote_by_id(quote.id)

    if result.state.fail:
        return RedirectResponse(
            url=f"/dashboard/quotes/{bot.id}?error_message=Failed to delete quote | reason: {result.state.name}",
            status_code=HTTPStatus.SEE_OTHER,
        )

    return RedirectResponse(
        url=f"/dashboard/quotes/{bot.id}?success_message=Quote deleted successfully",
        status_code=HTTPStatus.SEE_OTHER,
    )
