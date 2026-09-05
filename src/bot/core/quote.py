import random
import re

from discord.message import Message as DiscordMessage
from twitchAPI.chat import ChatMessage as TwitchMessage
from twitchAPI.helper import first

from bot.chat.helper.discord import get_user_by_id as get_discord_user_by_id
from bot.chat.helper.discord import get_user_by_name as get_discord_user_by_name
from bot.chat.helper.twitch import get_user_by_id as get_twitch_user_by_id
from bot.chat.helper.twitch import get_user_by_name as get_twitch_user_by_name
from bot.chat.twitch_chat import TwitchChat
from bot.chat.types.message import ChatMessage
from bot.core.discord_feature_flags import select_discord_feature_flags_by_server_id
from bot.core.twitch_feature_flags import select_twitch_feature_flags_by_channel_name
from bot.core.types.programm_parts import PROGRAMM_PARTS
from bot.core.types.result import Result
from bot.core.types.result import ResultState
from bot.database.quote import delete_quote as delete_quote_db
from bot.database.quote import insert_quote as insert_quote_db
from bot.database.quote import select_quote_by_bot_id as select_quote_by_bot_id_db
from bot.database.quote import select_quote_by_discord_id as select_quote_by_discord_id_db
from bot.database.quote import select_quote_by_id
from bot.database.quote import select_quote_by_twitch_id as select_quote_by_twitch_id_db
from bot.database.quote import update_quote as update_quote_db
from bot.database.types.quote import Quote
from bot.helpers.log import LogLevel
from bot.helpers.log import log_default


def is_active_quote(message: ChatMessage) -> bool:
    if message.has_twitch_message:
        if not isinstance(message.sender_chat, TwitchChat):
            return False
        flags = select_twitch_feature_flags_by_channel_name(message.bot_id, message.sender_chat.channel_name)
        if flags.state.success and flags.value:
            return flags.value.can_quote
    elif message.has_discord_message:
        server_id = message.try_get_discord_server_id()
        if server_id:
            flags = select_discord_feature_flags_by_server_id(message.bot_id, server_id)
            if flags.state.success and flags.value:
                return flags.value.can_quote
    return False


async def save_twitch_quote_by_message(text: str, message: ChatMessage) -> Result[int]:
    if not is_active_quote(message):
        return Result(ResultState.INACTIVE_FEATURE, None)

    if not isinstance(message.original_message, TwitchMessage):
        return Result(ResultState.TYPE_MISSMATCH, None)

    msg = text.strip()
    if not msg.startswith("@"):
        return Result(ResultState.MISSING_DATA, None)

    parts = msg[1:].split(maxsplit=1)
    if not parts:
        return Result(ResultState.MISSING_DATA, None)

    username = parts[0]
    quote = parts[1].strip() if len(parts) > 1 else ""

    if not quote:
        return Result(ResultState.MISSING_DATA, None)

    if PROGRAMM_PARTS.twitch is None:
        return Result(ResultState.ERROR, None)

    user = await first(PROGRAMM_PARTS.twitch.client.get_users(logins=[username]))
    if not user:
        return Result(ResultState.USER_NOT_FOUND, None)

    twitch_user_id = user.id

    return insert_quote_db(bot_id=message.bot_id, discord_id=None, twitch_id=twitch_user_id, quote=quote)


async def save_discord_quote_by_message(text: str, message: ChatMessage) -> Result[int]:
    if not is_active_quote(message):
        return Result(ResultState.INACTIVE_FEATURE, None)

    if not isinstance(message.original_message, DiscordMessage):
        return Result(ResultState.TYPE_MISSMATCH, None)

    msg = text.strip()
    if not msg.startswith("<@"):
        return Result(ResultState.MISSING_DATA, None)

    parts = msg.split(maxsplit=1)
    if len(parts) < 2:
        return Result(ResultState.MISSING_DATA, None)

    quote = parts[1].strip()
    if not quote:
        return Result(ResultState.MISSING_DATA, None)

    mentions = message.original_message.mentions
    if not mentions:
        return Result(ResultState.USER_NOT_FOUND, None)

    discord_user_id = mentions[0].id

    return insert_quote_db(bot_id=message.bot_id, discord_id=discord_user_id, twitch_id=None, quote=quote)


async def save_quote_by_message(text: str, message: ChatMessage) -> Result[int]:
    if not is_active_quote(message):
        return Result(ResultState.INACTIVE_FEATURE, None)

    if not message.original_message:
        return Result(ResultState.TYPE_MISSMATCH, None)

    if message.has_twitch_message:
        return await save_twitch_quote_by_message(text, message)

    if message.has_discord_message:
        return await save_discord_quote_by_message(text, message)

    return Result(ResultState.TYPE_MISSMATCH, None)


async def get_quotes_by_bot_id(bot_id: int) -> Result[list[Quote]]:
    return select_quote_by_bot_id_db(bot_id)


async def get_quote(text: str, message: ChatMessage) -> Result[str]:
    if not is_active_quote(message):
        return Result(ResultState.INACTIVE_FEATURE, None)

    async def get_random_quote() -> Result[str]:
        result = select_quote_by_bot_id_db(message.bot_id)
        if result.state.fail or result.value is None or not result.value:
            return Result(ResultState.NO_DATA, None)

        quotes = result.value

        # TODO: temporary debug logging for the "same quote after every idle pause" bug - remove once diagnosed
        rng_state_before = random.getstate()[1]
        quote_obj = random.choice(quotes)
        log_default(
            LogLevel.INFO,
            f"quote-debug | text={message.text!r} | n={len(quotes)} | ids={[quote.id for quote in quotes]}"
            + f" | chosen_id={quote_obj.id} | chosen_idx={quotes.index(quote_obj)}"
            + f" | mt_pos={rng_state_before[624]} | mt0={rng_state_before[0]} | mt623={rng_state_before[623]}",
        )

        return await format_quote(quote_obj)

    async def format_quote(quote: Quote) -> Result[str]:
        name = "Unknown"

        if quote.discord_user_id:
            user_res = await get_discord_user_by_id(quote.discord_user_id)
            if user_res.state.success and user_res.value:
                name = user_res.value.name
        elif quote.twitch_user_id:
            user_res = await get_twitch_user_by_id(quote.twitch_user_id)
            if user_res.state.success and user_res.value:
                name = user_res.value.display_name

        date_str = quote.timestamp.strftime("%d.%m.%Y")
        quote_str = f" {quote.quote} " if message.has_twitch_message else quote.quote
        return Result(ResultState.SUCCESS, f'{name} | {date_str}: "{quote_str}"')

    async def quote_lookup(text: str, message: ChatMessage) -> Result[str]:
        lookup_text = text.strip()
        if not lookup_text:
            return await get_random_quote()

        # Twitch lookup
        if message.has_twitch_message:
            if lookup_text.startswith("@"):
                username = lookup_text[1:].split()[0]
                user_res = await get_twitch_user_by_name(username)
                if user_res.state.success and user_res.value:
                    quotes_res = select_quote_by_twitch_id_db(message.bot_id, user_res.value.id)
                    if quotes_res.state.success and quotes_res.value:
                        return await format_quote(random.choice(quotes_res.value))
                    return Result(ResultState.NO_QUOTES_FOUND, None)
                return Result(ResultState.USER_NOT_FOUND, None)

        # Discord lookup
        if message.has_discord_message:
            # Check for mention <@ID> or <@!ID>
            match = re.match(r"<@!?(\d+)>", lookup_text)
            if match:
                user_id = int(match.group(1))
                quotes_res = select_quote_by_discord_id_db(bot_id=message.bot_id, discord_id=user_id)
                if quotes_res.state.success and quotes_res.value:
                    return await format_quote(random.choice(quotes_res.value))
                return Result(ResultState.NO_QUOTES_FOUND, None)

            # Fallback to name lookup if it's not a mention but some text
            user_res = await get_discord_user_by_name(lookup_text)
            if user_res.state.success and user_res.value:
                quotes_res = select_quote_by_discord_id_db(bot_id=message.bot_id, discord_id=user_res.value.id)
                if quotes_res.state.success and quotes_res.value:
                    return await format_quote(random.choice(quotes_res.value))
                return Result(ResultState.NO_QUOTES_FOUND, None)
            return Result(ResultState.USER_NOT_FOUND, None)

        return await get_random_quote()

    return await quote_lookup(text, message)


def get_quote_by_id(resource_id: int) -> Result[Quote]:
    return select_quote_by_id(resource_id)


def edit_quote_by_id(quote_id: int, quote: str) -> Result[None]:
    return update_quote_db(quote_id, quote)


def delete_quote_by_id(quote_id: int) -> Result[None]:
    return delete_quote_db(quote_id)
