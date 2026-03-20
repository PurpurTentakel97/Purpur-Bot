from typing import Final
from typing import Optional

from fastapi import APIRouter
from fastapi import Depends

from bot.chat.helper.discord import get_user_by_id as get_discord_user_by_id
from bot.chat.helper.twitch import get_user_by_id as get_twitch_user_by_id
from bot.frontend.helpers.auth import get_authenticated_twitch_user

router: Final = APIRouter(prefix="/api", dependencies=[Depends(get_authenticated_twitch_user)])


@router.get("/twitch/name/{user_id}")
async def get_twitch_name(user_id: str) -> Optional[str]:
    result = await get_twitch_user_by_id(user_id)
    if result.state.success and result.value:
        return result.value.display_name
    return None


@router.get("/discord/name/{user_id}")
async def get_discord_name(user_id: int) -> Optional[str]:
    result = await get_discord_user_by_id(user_id)
    if result.state.success and result.value:
        return result.value.name
    return None
