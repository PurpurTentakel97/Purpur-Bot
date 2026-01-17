from http import HTTPStatus
from typing import Annotated
from typing import Final

from fastapi import APIRouter
from fastapi import Depends
from fastapi.responses import JSONResponse
from starlette.requests import Request

from bot.core.app_context import APP_CONTEXT
from bot.core.bot import add_bot as add_bot_core
from bot.core.bot import delete_bot as delete_bot_core
from bot.core.bot import update_bot as update_bot_core
from bot.core.discord import add_discord_bot as add_discord_bot_core
from bot.core.discord import delete_discord_bot as delete_discord_bot_core
from bot.core.twitch import add_twitch_channel as add_twitch_channel_core
from bot.core.twitch import delete_twitch_channel as delete_twitch_channel_core
from bot.core.types.programm_parts import PROGRAMM_PARTS
from bot.frontend.helpers.auth import get_authenticated_discord_user
from bot.frontend.helpers.auth import get_authenticated_twitch_user
from bot.frontend.helpers.cast import to_int_or_raise
from bot.frontend.types.discord_user_info import DiscordUserInfo
from bot.frontend.types.twitch_user_info import TwitchUserInfo

router: Final = APIRouter(prefix="/api/bot", dependencies=[Depends(get_authenticated_twitch_user)])


# bot
@router.post("/create")
def new_bot(current_twitch_user: Annotated[TwitchUserInfo, Depends(get_authenticated_twitch_user)]) -> JSONResponse:
    try:
        result = add_bot_core(current_twitch_user.id_)
        if result.value is None:
            return JSONResponse(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                content={"message": f"Failed to create a bot | reason: {result.state.name}"},
            )

        return JSONResponse(status_code=HTTPStatus.CREATED, content={"id": result.value})

    except Exception as e:
        return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"message": str(e)})


@router.post("/edit")
async def edit_bot(
    request: Request,
) -> JSONResponse:
    try:
        data = await request.json()
        bot_id = to_int_or_raise(data.get("bot_id"))
        new_name = data.get("name")

        result = update_bot_core(bot_id, new_name)

        if result.state.fail:
            return JSONResponse(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                content={"message": f"Failed to update bot | reason: {result.state.name}"},
            )

        return JSONResponse(status_code=HTTPStatus.OK, content={"message": "Bot updated successfully"})

    except Exception as e:
        return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"message": str(e)})


@router.post("/delete")
async def delete_bot(request: Request) -> JSONResponse:
    try:
        data = await request.json()
        bot_id = to_int_or_raise(data.get("bot_id"))

        result = await delete_bot_core(bot_id)

        if result.state.fail:
            return JSONResponse(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                content={"message": f"Failed to delete a bot | reason: {result.state.name}"},
            )
        return JSONResponse(status_code=HTTPStatus.OK, content={"message": "Bot deleted successfully"})

    except Exception as e:
        return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"message": str(e)})


# Twitch
@router.post("/twitch/add")
async def add_twitch_channel(request: Request) -> JSONResponse:
    try:
        data = await request.json()
        bot_id = to_int_or_raise(data.get("bot_id"))
        twitch_channel = data.get("twitch_channel")

        result = await add_twitch_channel_core(bot_id, twitch_channel)

        if result.state.fail:
            return JSONResponse(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                content={"message": "Failed to add a twitch channel to bot"},
            )
        return JSONResponse(
            status_code=HTTPStatus.OK,
            content={"message": f"Twitch channel added successfully | reason: {result.state.name}"},
        )

    except Exception as e:
        return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"message": str(e)})


@router.post("/twitch/delete")
async def delete_twitch_channel(request: Request) -> JSONResponse:
    try:
        data = await request.json()
        bot_id = to_int_or_raise(data.get("bot_id"))
        twitch_channel = data.get("twitch_channel")

        result = await delete_twitch_channel_core(bot_id, twitch_channel)

        if result.state.fail:
            return JSONResponse(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                content={"message": f"Failed to delete twitch channel | reason: {result.state.name}"},
            )
        return JSONResponse(status_code=HTTPStatus.OK, content={"message": "Twitch channel deleted successfully"})

    except Exception as e:
        return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"message": str(e)})


# Discord
@router.post("/discord/add")
async def add_discord_server(
    request: Request,
    current_discord_user: Annotated[
        DiscordUserInfo, Depends(get_authenticated_discord_user)
    ],  # discord user for authentication
) -> JSONResponse:
    try:
        data = await request.json()
        bot_id = to_int_or_raise(data.get("bot_id"))
        server_id = to_int_or_raise(data.get("server_id"))
        server_name = data.get("server_name")

        result = add_discord_bot_core(bot_id, server_id, server_name)

        if result.state.fail:
            return JSONResponse(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                content={"message": f"Failed to add a discord server to bot | reason: {result.state.name}"},
            )

        invite_link = None
        if PROGRAMM_PARTS.discord is not None:
            guild = PROGRAMM_PARTS.discord.get_guild(int(server_id))
            if guild is None:
                # Bot is not on the server, generate an invite link
                client_id = APP_CONTEXT.discord_client_id.value_unsafe() or ""
                permissions = 8  # Administrator
                invite_link = f"https://discord.com/api/oauth2/authorize?client_id={client_id}&permissions={permissions}&scope=bot&guild_id={server_id}&disable_guild_select=true"

        return JSONResponse(
            status_code=HTTPStatus.OK,
            content={"message": "Discord server added successfully", "invite_link": invite_link},
        )

    except Exception as e:
        return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"message": str(e)})


@router.post("/discord/delete")
async def delete_discord_server(
    request: Request,
    current_discord_user: Annotated[
        DiscordUserInfo, Depends(get_authenticated_discord_user)
    ],  # discord user for authentication
) -> JSONResponse:
    try:
        data = await request.json()
        bot_id = to_int_or_raise(data.get("bot_id"))
        server_id = to_int_or_raise(data.get("server_id"))

        result = await delete_discord_bot_core(bot_id, server_id)

        if result.state.fail:
            return JSONResponse(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                content={"message": f"Failed to delete discord server | reason: {result.state.name}"},
            )
        return JSONResponse(status_code=HTTPStatus.OK, content={"message": "Discord server deleted successfully"})

    except Exception as e:
        return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"message": str(e)})
