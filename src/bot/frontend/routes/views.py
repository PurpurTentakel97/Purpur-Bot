from typing import Annotated
from typing import Final
from typing import Optional

from fastapi import APIRouter
from fastapi import Depends
from starlette.requests import Request
from starlette.responses import Response
from starlette.templating import Jinja2Templates

from bot.core.alias_dict import get_alias_dict_from_bot as get_alias_dict_from_bot_core
from bot.core.bot import get_all_active_bots as get_all_active_bots_core
from bot.core.commands import get_commands_by_bot_id as get_commands_by_bot_id_core
from bot.core.counter import get_counters_by_bot_id as get_counters_by_bot_id_core
from bot.core.quote import get_quotes_by_bot_id as get_quotes_by_bot_id_core
from bot.database.types.bot_config import BotConfigDB
from bot.frontend.helpers.decorators import get_bot
from bot.frontend.helpers.decorators import get_optional_owned_discord_user
from bot.frontend.helpers.decorators import get_optional_owned_twitch_user
from bot.frontend.helpers.decorators import get_owned_discord_user
from bot.frontend.helpers.decorators import get_owned_twitch_user
from bot.frontend.helpers.route_utils import get_templates
from bot.frontend.types.discord_user_info import DiscordUserInfo
from bot.frontend.types.twitch_user_info import TwitchUserInfo

router: Final = APIRouter(prefix="/view")


@router.get("/")
async def view(
    request: Request,
    template: Annotated[Jinja2Templates, Depends(get_templates)],
    twitch_user: Annotated[Optional[TwitchUserInfo], Depends(get_optional_owned_twitch_user)],
    discord_user: Annotated[Optional[DiscordUserInfo], Depends(get_optional_owned_discord_user)],
) -> Response:
    bots_result: Final = get_all_active_bots_core()
    bots = bots_result.value if bots_result.state.success and bots_result.value else []
    bots.sort(key=lambda b: b.name.lower())

    return template.TemplateResponse(
        request=request,
        name="view.html",
        context={
            "bots": bots,
            "twitch_user": twitch_user,
            "discord_user": discord_user,
        },
    )


@router.get("/{bot_id:int}/")
async def view_main(
    request: Request,
    bot: Annotated[BotConfigDB, Depends(get_bot)],
    template: Annotated[Jinja2Templates, Depends(get_templates)],
    twitch_user: Annotated[Optional[TwitchUserInfo], Depends(get_optional_owned_twitch_user)],
    discord_user: Annotated[Optional[DiscordUserInfo], Depends(get_optional_owned_discord_user)],
) -> Response:
    return template.TemplateResponse(
        request=request,
        name="view_main.html",
        context={
            "bot": bot,
            "twitch_user": twitch_user,
            "discord_user": discord_user,
        },
    )


@router.get("/{bot_id:int}/commands")
async def view_commands(
    request: Request,
    bot: Annotated[BotConfigDB, Depends(get_bot)],
    template: Annotated[Jinja2Templates, Depends(get_templates)],
    twitch_user: Annotated[Optional[TwitchUserInfo], Depends(get_owned_twitch_user)],
    discord_user: Annotated[Optional[DiscordUserInfo], Depends(get_owned_discord_user)],
) -> Response:
    commands_result: Final = get_commands_by_bot_id_core(bot.id)
    return template.TemplateResponse(
        request=request,
        name="view_commands.html",
        context={
            "commands": commands_result.value or [],
            "bot": bot,
            "twitch_user": twitch_user,
            "discord_user": discord_user,
        },
    )


@router.get("/{bot_id:int}/counter")
async def view_counter(
    request: Request,
    bot: Annotated[BotConfigDB, Depends(get_bot)],
    template: Annotated[Jinja2Templates, Depends(get_templates)],
    twitch_user: Annotated[Optional[TwitchUserInfo], Depends(get_owned_twitch_user)],
    discord_user: Annotated[Optional[DiscordUserInfo], Depends(get_owned_discord_user)],
) -> Response:
    counter_result: Final = get_counters_by_bot_id_core(bot.id)
    return template.TemplateResponse(
        request=request,
        name="view_counter.html",
        context={
            "counter": counter_result.value or [],
            "bot": bot,
            "twitch_user": twitch_user,
            "discord_user": discord_user,
        },
    )


@router.get("/{bot_id:int}/alias")
async def view_alias(
    request: Request,
    bot: Annotated[BotConfigDB, Depends(get_bot)],
    template: Annotated[Jinja2Templates, Depends(get_templates)],
    twitch_user: Annotated[Optional[TwitchUserInfo], Depends(get_optional_owned_twitch_user)],
    discord_user: Annotated[Optional[DiscordUserInfo], Depends(get_optional_owned_discord_user)],
) -> Response:
    aliases_result: Final = get_alias_dict_from_bot_core(bot.id)
    return template.TemplateResponse(
        request=request,
        name="view_alias.html",
        context={
            "aliases": aliases_result.value or [],
            "bot": bot,
            "twitch_user": twitch_user,
            "discord_user": discord_user,
        },
    )


@router.get("/{bot_id:int}/quote")
async def view_quote(
    request: Request,
    bot: Annotated[BotConfigDB, Depends(get_bot)],
    template: Annotated[Jinja2Templates, Depends(get_templates)],
    twitch_user: Annotated[Optional[TwitchUserInfo], Depends(get_optional_owned_twitch_user)],
    discord_user: Annotated[Optional[DiscordUserInfo], Depends(get_optional_owned_discord_user)],
) -> Response:
    quotes_result: Final = await get_quotes_by_bot_id_core(bot.id)
    return template.TemplateResponse(
        request=request,
        name="view_quote.html",
        context={
            "quotes": quotes_result.value or [],
            "bot": bot,
            "twitch_user": twitch_user,
            "discord_user": discord_user,
        },
    )
