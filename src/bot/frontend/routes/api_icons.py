from datetime import UTC
from datetime import datetime
from datetime import timedelta
from typing import Annotated
from typing import Final
from typing import Optional

import httpx
from fastapi import APIRouter
from fastapi import Depends
from starlette.responses import Response
from twitchAPI.helper import first
from twitchAPI.twitch import Twitch

from bot.core.app_context import APP_CONTEXT
from bot.frontend.helpers.auth import get_discord_user
from bot.frontend.helpers.auth import get_twitch_user
from bot.frontend.types.discord_user_info import DiscordUserInfo
from bot.frontend.types.twitch_user_info import TwitchUserInfo
from bot.helpers.log import LogProgram
from bot.helpers.log import log_exception

router: APIRouter = APIRouter(prefix="/icons")

# Cache for twitch icons: user_id -> (image_bytes, content_type, timestamp)
TWITCH_ICON_CACHE: Final[dict[str, tuple[bytes, str, datetime]]] = {}

# Cache for discord icons: user_id -> (image_bytes, content_type, timestamp)
DISCORD_ICON_CACHE: Final[dict[int, tuple[bytes, str, datetime]]] = {}

# Transparent 1x1 pixel PNG
TRANSPARENT_PIXEL: Final[bytes] = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    + b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01"
    + b"\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
)


@router.get("/twitch/profile_icon")
async def get_twitch_icon(
    twitch_user: Annotated[Optional[TwitchUserInfo], Depends(get_twitch_user)],
) -> Response:
    if twitch_user is None:
        return Response(content=TRANSPARENT_PIXEL, media_type="image/png")

    now = datetime.now(UTC)
    user_id = twitch_user.id_

    if user_id in TWITCH_ICON_CACHE:
        image_bytes, content_type, timestamp = TWITCH_ICON_CACHE[user_id]
        if now - timestamp < timedelta(minutes=30):
            return Response(
                content=image_bytes, media_type=content_type, headers={"Cache-Control": "public, max-age=1800"}
            )

    try:
        twitch = await Twitch(
            APP_CONTEXT.twitch_client_id.value_or_rise(),
            APP_CONTEXT.twitch_credentials.value_or_rise(),
        )
        try:
            user = await first(twitch.get_users(user_ids=[user_id]))
            if user is None:
                return Response(content=TRANSPARENT_PIXEL, media_type="image/png")

            async with httpx.AsyncClient() as client:
                img_response = await client.get(user.profile_image_url)
                img_response.raise_for_status()
                image_bytes = img_response.content
                content_type = img_response.headers.get("Content-Type", "image/png")

            TWITCH_ICON_CACHE[user_id] = (image_bytes, content_type, now)
            return Response(
                content=image_bytes, media_type=content_type, headers={"Cache-Control": "public, max-age=1800"}
            )
        finally:
            await twitch.close()
    except Exception as e:
        log_exception(e, LogProgram.Frontend, f"Failed to fetch Twitch icon for user {user_id}")
        return Response(content=TRANSPARENT_PIXEL, media_type="image/png")


@router.get("/discord/profile_icon")
async def get_discord_icon(discord_user: Annotated[Optional[DiscordUserInfo], Depends(get_discord_user)]) -> Response:
    if discord_user is None:
        return Response(content=TRANSPARENT_PIXEL, media_type="image/png")

    now = datetime.now(UTC)
    user_id = discord_user.id_

    if user_id in DISCORD_ICON_CACHE:
        image_bytes, content_type, timestamp = DISCORD_ICON_CACHE[user_id]
        if now - timestamp < timedelta(minutes=30):
            return Response(
                content=image_bytes, media_type=content_type, headers={"Cache-Control": "public, max-age=1800"}
            )

    try:
        async with httpx.AsyncClient() as client:
            img_response = await client.get(discord_user.avatar_url)
            img_response.raise_for_status()
            image_bytes = img_response.content
            content_type = img_response.headers.get("Content-Type", "image/png")

        DISCORD_ICON_CACHE[user_id] = (image_bytes, content_type, now)
        return Response(content=image_bytes, media_type=content_type, headers={"Cache-Control": "public, max-age=1800"})
    except Exception as e:
        log_exception(e, LogProgram.Frontend, f"Failed to fetch Discord icon for user {user_id}")
        return Response(content=TRANSPARENT_PIXEL, media_type="image/png")
