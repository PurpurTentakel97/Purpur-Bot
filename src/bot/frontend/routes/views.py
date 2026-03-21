from typing import Final, Annotated, Optional

from fastapi import APIRouter, Depends
from starlette.requests import Request
from starlette.responses import Response
from starlette.templating import Jinja2Templates

from bot.core.alias_dict import get_alias_dict_from_bot as get_alias_dict_from_bot_core
from bot.core.counter import get_counters_by_bot_id as get_counters_by_bot_id_core
from bot.core.quote import get_quotes_by_bot_id as get_quotes_by_bot_id_core
from bot.database.types.bot_config import BotConfigDB
from bot.frontend.helpers.auth import get_twitch_user, get_discord_user
from bot.frontend.helpers.route_utils import get_valid_bot, get_templates
from bot.frontend.types.discord_user_info import DiscordUserInfo
from bot.frontend.types.twitch_user_info import TwitchUserInfo
from bot.core.commands import get_commands_by_bot_id as get_commands_by_bot_id_core

router: Final = APIRouter(prefix="/view/{bot_id:int}")

@router.get("/")
async def view_main(
    request: Request,
    bot: Annotated[BotConfigDB, Depends(get_valid_bot)],
    template: Annotated[Jinja2Templates, Depends(get_templates)],
    twitch_user: Annotated[Optional[TwitchUserInfo], Depends(get_twitch_user)],
    discord_user: Annotated[Optional[DiscordUserInfo], Depends(get_discord_user)],
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

@router.get("/commands")
async def view_commands(
    request: Request,
    bot: Annotated[BotConfigDB, Depends(get_valid_bot)],
    template: Annotated[Jinja2Templates, Depends(get_templates)],
    twitch_user: Annotated[Optional[TwitchUserInfo], Depends(get_twitch_user)],
    discord_user: Annotated[Optional[DiscordUserInfo], Depends(get_discord_user)],
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


@router.get("/counter")
async def view_counter(
    request: Request,
    bot: Annotated[BotConfigDB, Depends(get_valid_bot)],
    template: Annotated[Jinja2Templates, Depends(get_templates)],
    twitch_user: Annotated[Optional[TwitchUserInfo], Depends(get_twitch_user)],
    discord_user: Annotated[Optional[DiscordUserInfo], Depends(get_discord_user)],
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


@router.get("/alias")
async def view_alias(
    request: Request,
    bot: Annotated[BotConfigDB, Depends(get_valid_bot)],
    template: Annotated[Jinja2Templates, Depends(get_templates)],
    twitch_user: Annotated[Optional[TwitchUserInfo], Depends(get_twitch_user)],
    discord_user: Annotated[Optional[DiscordUserInfo], Depends(get_discord_user)],
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


@router.get("/quote")
async def view_quote(
    request: Request,
    bot: Annotated[BotConfigDB, Depends(get_valid_bot)],
    template: Annotated[Jinja2Templates, Depends(get_templates)],
    twitch_user: Annotated[Optional[TwitchUserInfo], Depends(get_twitch_user)],
    discord_user: Annotated[Optional[DiscordUserInfo], Depends(get_discord_user)],
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
