from typing import Optional

from bot.chat.types.message import ChatMessage
from bot.chat.types.message_response import ChatMessageResponse
from bot.core.alias_dict import add_alias as add_alias_core
from bot.core.alias_dict import delete_alias as delete_alias_core
from bot.core.alias_dict import disable_alias_by_bot_id as disable_alias_by_bot_id_core
from bot.core.alias_dict import edit_dict_alias as edit_dict_alias_core
from bot.core.alias_dict import edit_dict_explanation as edit_dict_explanation_core
from bot.core.alias_dict import enable_alias_by_bot_id as enable_alias_by_bot_id_core
from bot.core.commands import delete_command as delete_command_core
from bot.core.commands import disable_command_by_bot_id as disable_command_by_bot_id_core
from bot.core.commands import enable_command_by_bot_id as enable_command_by_bot_id_core
from bot.core.commands import get_command_with_counter as get_command_core
from bot.core.commands import save_command as save_command_core
from bot.core.commands import update_command_message as update_command_message_core
from bot.core.commands import update_command_name as update_command_name_core
from bot.core.counter import decrement_counter as decrement_counter_core
from bot.core.counter import decrement_counter_by as decrement_counter_by_core
from bot.core.counter import delete_counter as delete_counter_core
from bot.core.counter import edit_counter_name as edit_counter_name_core
from bot.core.counter import edit_counter_value as edit_counter_value_core
from bot.core.counter import get_counter as get_counter_core
from bot.core.counter import increment_counter as increment_counter_core
from bot.core.counter import increment_counter_by as increment_counter_by_core
from bot.core.counter import reset_counter as reset_counter_core
from bot.core.counter import save_counter as save_counter_core
from bot.core.quote import get_quote
from bot.core.quote import save_quote_by_message
from bot.core.types.cooldown import CommandCooldownKey
from bot.core.types.permission_level import PermissionLevel
from bot.core.types.programm_parts import PROGRAMM_PARTS
from bot.core.types.result import ResultState
from bot.database.types.feature_flags import FeatureFlagsDB
from bot.helpers.log import LogLevel
from bot.helpers.log import log_default


def _to_int(value: str) -> Optional[int]:
    try:
        return int(value)
    except ValueError:
        return None


def _result_lookup(state: ResultState) -> str:
    match state:
        case ResultState.WHITESPACE_ERROR:
            return "the identifier contains whitespace."
        case ResultState.ALREADY_EXISTS:
            return "the identifier already exists."
        case ResultState.EMPTY_NAME:
            return "the identifier is empty."
        case ResultState.EMPTY_MESSAGE:
            return "the message is empty."
        case ResultState.STILL_IN_USE:
            return "the identifier is still in use."
        case ResultState.NO_DATA:
            return "unknown identifier."
        case ResultState.RESERVED_NAME:
            return "the identifier is reserved."
        case ResultState.USER_NOT_FOUND:
            return "user not found."
        case ResultState.NO_QUOTES_FOUND:
            return "this user does not have any Quotes."
        case ResultState.INACTIVE_FEATURE:
            return "this feature is not enabled."
        case _:
            return "internal error"


async def handle_command(message: ChatMessage, feature_flags: FeatureFlagsDB) -> Optional[ChatMessageResponse]:
    parts = message.text.strip().split(" ")
    if len(parts) == 0:
        log_default(LogLevel.ERROR, f"the command is empty. Ignoring command. | message: '{message}'")
        return None

    # permission level admin
    # currently there are no admin level commands

    # permission level moderator
    if message.sender_permission_level.is_permitted(PermissionLevel.MODERATOR):
        match parts:
            # twitch-specific commands
            case ["!title", *title]:
                if not message.has_twitch_message:
                    return message.to_response_message("This command is only available in Twitch Chats.")
                if PROGRAMM_PARTS.twitch is None:
                    return message.to_response_message("Twitch bot is not running.")

                broadcaster_id = message.try_get_twitch_broadcaster_id()
                if broadcaster_id is None:
                    return message.to_response_message("Failed to get broadcaster ID.")

                new_title = " ".join(title)
                if not new_title:
                    return message.to_response_message("Invalid title. Use '!title <new_title>'")

                return await PROGRAMM_PARTS.twitch.send_change_title(message, broadcaster_id, new_title)

            case ["!game", *game]:
                if not message.has_twitch_message:
                    return message.to_response_message("This command is only available in Twitch chat.")
                if PROGRAMM_PARTS.twitch is None:
                    return message.to_response_message("Twitch bot is not running.")

                broadcaster_id = message.try_get_twitch_broadcaster_id()
                if not broadcaster_id:
                    return message.to_response_message("Failed to get broadcaster ID.")

                new_game = " ".join(game)
                if not new_game:
                    return message.to_response_message("Invalid game. Use '!game <new_game>'")

                return await PROGRAMM_PARTS.twitch.send_change_game(message, broadcaster_id, new_game)

            case ["!tags", *tags]:
                if not message.has_twitch_message:
                    return message.to_response_message("This command is only available in Twitch chat.")

                if PROGRAMM_PARTS.twitch is None:
                    return message.to_response_message("Twitch bot is not running.")

                broadcaster_id = message.try_get_twitch_broadcaster_id()
                if not broadcaster_id:
                    return message.to_response_message("Failed to get broadcaster ID.")

                if not tags:
                    return message.to_response_message("Invalid tags. Use '!tags <tag1> <tag2> ...'")

                return await PROGRAMM_PARTS.twitch.send_change_tags(message, broadcaster_id, tags)

            case _:
                pass

    # permission level special user
    if message.sender_permission_level.is_permitted(PermissionLevel.SPECIAL_USER):
        match parts:
            # command
            case ["!com", "add", command_name, *msg]:
                command_message = " ".join(msg)
                result = save_command_core(message.bot_id, command_name, command_message)
                if result.state.success and result.value is not None:
                    return message.to_response_message(f"Command '{result.value.command}' saved successfully.")
                return message.to_response_message(f"Failed to save command: {_result_lookup(result.state)}")

            case ["!com", "edit_message", command_name, *msg]:
                command_message = " ".join(msg)
                result = update_command_message_core(message.bot_id, command_name, command_message)
                if result.state.success and result.value is not None:
                    return message.to_response_message(f"Command '{result.value.command}' edited successfully.")
                return message.to_response_message(f"Failed to edit command message: {_result_lookup(result.state)}")

            case ["!com", "edit_name", old_command_name, new_command_name, *_]:
                result = update_command_name_core(message.bot_id, old_command_name, new_command_name)
                if result.state.success and result.value is not None:
                    return message.to_response_message(
                        f"Command '{old_command_name.strip().lower()}'"
                        + f" renamed successfully to '{result.value.command}'."
                    )
                return message.to_response_message(f"Failed to rename command: {_result_lookup(result.state)}")

            case ["!com", "enable", command_name, *_]:
                result = enable_command_by_bot_id_core(message.bot_id, command_name)
                if result.state.success and result.value is not None:
                    return message.to_response_message(f"Command '{result.value.command}' enabled successfully.")
                return message.to_response_message(f"Failed to enable command: {_result_lookup(result.state)}")

            case ["!com", "disable", command_name, *_]:
                result = disable_command_by_bot_id_core(message.bot_id, command_name)
                if result.state.success and result.value is not None:
                    return message.to_response_message(f"Command '{result.value.command}' disabled successfully.")
                return message.to_response_message(f"Failed to disable command: {_result_lookup(result.state)}")

            case ["!com", "remove", command_name, *_]:
                result = delete_command_core(message.bot_id, command_name)
                if result.state.success:
                    return message.to_response_message(
                        f"Command '{command_name.strip().lower()}' deleted successfully."
                    )
                return message.to_response_message(f"Failed to delete command: {_result_lookup(result.state)}")

            case ["!com", *_]:
                return message.to_response_message(
                    "Invalid command format. Use '!com add|edit|remove <command_name> <command_message>'"
                )

            # counter
            case ["!counter", "add", counter_name, *_]:
                result = save_counter_core(message.bot_id, counter_name)
                if result.state.success and result.value is not None:
                    return message.to_response_message(f"Counter '{result.value.name}' created successfully.")
                return message.to_response_message(f"Failed to create counter: {_result_lookup(result.state)}")

            case ["!counter", "reset", counter_name, *_]:
                result = reset_counter_core(message.bot_id, counter_name)
                if result.state.success and result.value is not None:
                    return message.to_response_message(f"Counter '{result.value.name}' reset successfully.")
                return message.to_response_message(f"Failed to reset counter: {_result_lookup(result.state)}")

            case ["!counter", "remove", counter_name, *_]:
                result = delete_counter_core(message.bot_id, counter_name)
                if result.state.success:
                    return message.to_response_message(
                        f"Counter '{counter_name.strip().lower()}' deleted successfully."
                    )
                return message.to_response_message(f"Failed to delete counter: {_result_lookup(result.state)}")

            case ["!counter", "show", counter_name, *_]:
                result = get_counter_core(message.bot_id, counter_name)
                if result.state.success and result.value is not None:
                    return message.to_response_message(f"Counter '{result.value.name}': {result.value.count}")
                return message.to_response_message(f"Failed to show counter: {_result_lookup(result.state)}")

            case ["!counter", "increment", counter_name, *_]:
                result = increment_counter_core(message.bot_id, counter_name)
                if result.state.success and result.value is not None:
                    return message.to_response_message(
                        f"Counter '{result.value.name}' incremented successfully to '{result.value.count}'."
                    )
                return message.to_response_message(f"Failed to increment counter: {_result_lookup(result.state)}")

            case ["!counter", "increment_by", counter_name, value, *_]:
                v = _to_int(value)
                if v is None:
                    return message.to_response_message("Invalid value. Must be a number.")

                result = increment_counter_by_core(message.bot_id, counter_name, v)
                if result.state.success and result.value is not None:
                    return message.to_response_message(
                        f"Counter '{result.value.name}' incremented by '{v}' successfully to '{result.value.count}'."
                    )
                return message.to_response_message(f"Failed to increment counter: {_result_lookup(result.state)}")

            case ["!counter", "decrement", counter_name, *_]:
                result = decrement_counter_core(message.bot_id, counter_name)
                if result.state.success and result.value is not None:
                    return message.to_response_message(
                        f"Counter '{result.value.name}' decremented successfully to '{result.value.count}'."
                    )
                return message.to_response_message(f"Failed to decrement counter: {_result_lookup(result.state)}")

            case ["!counter", "decrement_by", counter_name, value, *_]:
                v = _to_int(value)
                if v is None:
                    return message.to_response_message("Invalid value. Must be a number.")

                result = decrement_counter_by_core(message.bot_id, counter_name, v)
                if result.state.success and result.value is not None:
                    return message.to_response_message(
                        f"Counter '{result.value.name}' decremented by '{v}' successfully to '{result.value.count}'."
                    )
                return message.to_response_message(f"Failed to decrement counter: {_result_lookup(result.state)}")

            case ["!counter", "edit_count", counter_name, value, *_]:
                v = _to_int(value)
                if v is None:
                    return message.to_response_message("Invalid value. Must be a number.")

                result = edit_counter_value_core(message.bot_id, counter_name, v)
                if result.state.success and result.value is not None:
                    return message.to_response_message(f"Counter '{result.value.name}' set to '{result.value.count}'.")
                return message.to_response_message(f"Failed to set counter value: {_result_lookup(result.state)}")

            case ["!counter", "edit_name", counter_name, new_name, *_]:
                result = edit_counter_name_core(message.bot_id, counter_name, new_name)
                if result.state.success and result.value is not None:
                    return message.to_response_message(
                        f"Counter '{result.value.name}' renamed to '{result.value.name}'."
                    )
                return message.to_response_message(f"Failed to rename counter: {_result_lookup(result.state)}")

            case ["!counter", *_]:
                return message.to_response_message(
                    "Invalid command format. Use '!counter"
                    + " add|reset|remove|show|increment|decrement|edit_name|edit_count <counter_name> <new_value>'"
                )

            # dict
            case ["!alias", "add", alias, *msg]:
                command_message = " ".join(msg)
                result = add_alias_core(message.bot_id, alias, command_message)
                if result.state.success and result.value is not None:
                    return message.to_response_message(
                        f"Alias '{result.value.alias}' added with explanation '{result.value.explanation}'."
                    )
                return message.to_response_message(f"Failed to add alias: {_result_lookup(result.state)}")

            case ["!alias", "edit_name", old_alias, new_alias, *_]:
                result = edit_dict_alias_core(message.bot_id, old_alias, new_alias)
                if result.state.success and result.value is not None:
                    return message.to_response_message(f"Alias '{old_alias}' updated to '{new_alias}'.")
                return message.to_response_message(f"Failed to edit alias: {_result_lookup(result.state)}")

            case ["!alias", "edit_message", alias, *msg]:
                command_message = " ".join(msg)
                result = edit_dict_explanation_core(message.bot_id, alias, command_message)
                if result.state.success and result.value is not None:
                    return message.to_response_message(f"Alias '{alias}' updated to explanation '{command_message}'.")
                return message.to_response_message(f"Failed to edit alias explanation: {_result_lookup(result.state)}")

            case ["!alias", "enable", alias, *_]:
                result = enable_alias_by_bot_id_core(message.bot_id, alias)
                if result.state.success and result.value is not None:
                    return message.to_response_message(f"Alias '{alias}' enabled successfully.")
                return message.to_response_message(f"Failed to enable alias: {_result_lookup(result.state)}")

            case ["!alias", "disable", alias, *_]:
                result = disable_alias_by_bot_id_core(message.bot_id, alias)
                if result.state.success and result.value is not None:
                    return message.to_response_message(f"Alias '{alias}' disabled successfully.")
                return message.to_response_message(f"Failed to disable alias: {_result_lookup(result.state)}")

            case ["!alias", "remove", alias, *_]:
                result = delete_alias_core(message.bot_id, alias)
                if result.state.success:
                    return message.to_response_message(f"Alias '{alias}' deleted successfully.")
                return message.to_response_message(f"Failed to delete alias: {_result_lookup(result.state)}")

            case ["!alias", *_]:
                return message.to_response_message(
                    "Invalid command format. Use '!alias add|edit_name|edit_message|remove <alias> <new_value>'"
                )

            case _:
                pass

    # permission level user
    match parts:
        # quote
        case ["!quote", "add", *quote]:
            quote_text = " ".join(quote)
            result = await save_quote_by_message(quote_text, message)
            if result.state.success:
                return message.to_response_message("New Quote saved successfully.")
            return message.to_response_message(f"Failed to save quote: {_result_lookup(result.state)}")

        case ["!quote", name, *_]:
            result = await get_quote(name, message)
            if result.state.success and result.value is not None:
                return message.to_response_message(result.value)
            return message.to_response_message(f"Failed to get quote: {_result_lookup(result.state)}")

        case ["!quote", *_]:
            result = await get_quote("", message)
            if result.state.success and result.value is not None:
                return message.to_response_message(result.value)
            return message.to_response_message(f"Failed to get quote: {_result_lookup(result.state)}")

        case ["!coms", *_]:
            url = f"https://purpur-bot.coder2k.net/view/{message.bot_id}"
            return message.to_response_message(f"You can view all commands, counters, aliases and quotes here: {url}")

        case ["!help", *_]:
            url = "https://github.com/PurpurTentakel97/Purpur-Bot"
            return message.to_response_message(
                f"Help for Purpur Bot: {url} or enter !coms to view all commands from this bot."
            )
        case _:
            pass

    if feature_flags.can_commands:
        cooldown_key = CommandCooldownKey(
            message.bot_id,
            parts[0],
            message.try_get_twitch_broadcaster_id() or "",
            message.try_get_discord_server_id() or 0,
            message.try_get_discord_channel_id() or 0,
        )
        if PROGRAMM_PARTS.cooldowns.command_response_cooldown.is_in_cooldown(cooldown_key):
            log_default(LogLevel.DEBUG, f"command in Cooldown | message: '{message}'")
            return None

        result = get_command_core(message, parts[0].lstrip("!"))
        if result.state.success and result.value is not None:
            if not message.sender_permission_level.is_permitted(result.value.permission_level):
                return message.to_response_message(
                    "You are not allowed to use this command. This command has "
                    + f"{result.value.permission_level.name} permission level."
                )
            PROGRAMM_PARTS.cooldowns.command_response_cooldown.add(cooldown_key)
            return message.to_response_message(result.value.message)

    return None
