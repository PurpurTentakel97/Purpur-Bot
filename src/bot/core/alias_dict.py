from bot.core.helpers.string import check_identifier
from bot.core.helpers.string import check_text
from bot.core.helpers.string import identifier_for_db
from bot.core.types.cooldown import AliasCooldownKey
from bot.core.types.programm_parts import PROGRAMM_PARTS
from bot.core.types.result import Result
from bot.core.types.result import ResultState
from bot.database.alias_dict import delete_dict_entry as delete_dict_entry_db
from bot.database.alias_dict import delete_dict_entry_by_id as delete_dict_entry_by_id_db
from bot.database.alias_dict import insert_dict_entry as insert_dict_entry_db
from bot.database.alias_dict import select_dict_entry_by_id as select_dict_entry_by_id_db
from bot.database.alias_dict import select_dict_from_bot as select_dict_from_bot_db
from bot.database.alias_dict import update_dict_entry as update_dict_entry_db
from bot.database.alias_dict import update_dict_entry_by_id as update_dict_entry_by_id_db
from bot.database.types.alias_dict_entry import AliasDictEntry
from bot.database.types.fields import FIELD_ALIAS_EXPLANATION
from bot.database.types.fields import FIELD_ALIAS_NAME
from bot.database.types.fields import FIELD_ENABLED
from bot.helpers.log import LogLevel
from bot.helpers.log import log_default


def get_alias_dict_from_bot(bot_id: int) -> Result[list[AliasDictEntry]]:
    return select_dict_from_bot_db(bot_id)


def get_alias_by_id(entry_id: int) -> Result[AliasDictEntry]:
    return select_dict_entry_by_id_db(entry_id)


def alias_lookup(
    bot_id: int,
    message: str,
    twitch_broadcaster_id: str,
    discord_server_id: int,
    discord_channel_id: int,
) -> Result[list[str]]:
    alias_dict = select_dict_from_bot_db(bot_id)

    if alias_dict.state.fail or alias_dict.value is None or len(alias_dict.value) == 0:
        return alias_dict.cast_to(list[str], [])

    lookups: list[str] = []

    split_message = message.lower().split(" ")

    for entry in alias_dict.value:
        if not entry.enabled:
            continue

        if entry.alias in split_message:
            cooldown_key = AliasCooldownKey(
                bot_id,
                entry.alias,
                twitch_broadcaster_id,
                discord_server_id,
                discord_channel_id,
            )

            if PROGRAMM_PARTS.cooldowns.alias_response_cooldown.is_in_cooldown(cooldown_key):
                log_default(LogLevel.DEBUG, f"alias in Cooldown | alias: '{entry.alias}' | message: '{message}'")
                continue

            lookups.append(f"{entry.alias}: {entry.explanation}")
            PROGRAMM_PARTS.cooldowns.alias_response_cooldown.add(cooldown_key)

    return Result(ResultState.SUCCESS, lookups)


def add_alias(bot_id: int, alias: str, explanation: str) -> Result[AliasDictEntry]:
    alias_res = check_identifier(alias)
    explanation_res = check_text(explanation)

    if alias_res.state.fail or alias_res.value is None:
        return alias_res.cast_to(AliasDictEntry)
    if explanation_res.state.fail or explanation_res.value is None:
        return explanation_res.cast_to(AliasDictEntry)

    return insert_dict_entry_db(bot_id, alias_res.value, explanation_res.value)


def edit_dict_alias(bot_id: int, old_alias: str, new_alias: str) -> Result[AliasDictEntry]:
    old_alias_db = identifier_for_db(old_alias)
    new_alias_res = check_identifier(new_alias)

    if new_alias_res.state.fail or new_alias_res.value is None:
        return new_alias_res.cast_to(AliasDictEntry)

    return update_dict_entry_db(bot_id, old_alias_db, {FIELD_ALIAS_NAME: new_alias_res.value})


def edit_dict_explanation(bot_id: int, alias: str, explanation: str) -> Result[AliasDictEntry]:
    alias_db = identifier_for_db(alias)
    explanation_res = check_text(explanation)

    if explanation_res.state.fail or explanation_res.value is None:
        return explanation_res.cast_to(AliasDictEntry)

    return update_dict_entry_db(bot_id, alias_db, {FIELD_ALIAS_EXPLANATION: explanation_res.value})


def update_alias_by_id(entry_id: int, alias: str, explanation: str, enabled: bool) -> Result[AliasDictEntry]:
    alias_res = check_identifier(alias)
    explanation_res = check_text(explanation)

    if alias_res.state.fail or alias_res.value is None:
        return alias_res.cast_to(AliasDictEntry)
    if explanation_res.state.fail or explanation_res.value is None:
        return explanation_res.cast_to(AliasDictEntry)

    return update_dict_entry_by_id_db(
        entry_id,
        {FIELD_ALIAS_NAME: alias_res.value, FIELD_ALIAS_EXPLANATION: explanation_res.value, FIELD_ENABLED: enabled},
    )


def enable_alias_by_bot_id(bot_id: int, alias: str) -> Result[AliasDictEntry]:
    return update_dict_entry_db(bot_id, identifier_for_db(alias), {FIELD_ENABLED: True})


def disable_alias_by_bot_id(bot_id: int, alias: str) -> Result[AliasDictEntry]:
    return update_dict_entry_db(bot_id, identifier_for_db(alias), {FIELD_ENABLED: False})


def delete_alias(bot_id: int, alias: str) -> Result[None]:
    return delete_dict_entry_db(bot_id, identifier_for_db(alias))


def delete_alias_by_id(entry_id: int) -> Result[None]:
    return delete_dict_entry_by_id_db(entry_id)
