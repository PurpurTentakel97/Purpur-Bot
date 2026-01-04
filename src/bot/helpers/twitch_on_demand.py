from bot.chat.twitch_chat import TwitchChat
from bot.types.feature_flag import DEFAULT_TWITCH_FEATURES
from bot.types.programm_parts import PROGRAMM_PARTS


async def start_single_twitch_bot(id_: int, channel_name: str) -> bool:
    if PROGRAMM_PARTS.twitch is None:
        return False

    await TwitchChat.create(PROGRAMM_PARTS.twitch, id_, channel_name, DEFAULT_TWITCH_FEATURES)

    return True


async def stop_single_twitch_bot(id_: int, channel_name: str) -> bool:
    if PROGRAMM_PARTS.twitch is None:
        return False

    for channel in PROGRAMM_PARTS.twitch.chats:
        if channel.id == id_ and channel.channel_name == channel_name:
            await channel.terminate()
            return True

    return False
