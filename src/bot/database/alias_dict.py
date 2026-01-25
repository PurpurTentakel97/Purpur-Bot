from typing import Any

from bot.core.types.programm_parts import PROGRAMM_PARTS
from bot.core.types.result import Result
from bot.database.types.alias_dict_entry import AliasDictEntry
from bot.database.types.fields import FIELD_ALIAS_EXPLANATION
from bot.database.types.fields import FIELD_ALIAS_NAME
from bot.database.types.fields import FIELD_BOT_ID
from bot.database.types.fields import FIELD_ID
from bot.database.types.fields import TABLE_ALIAS_NAME


def select_dict_from_bot(bot_id: int) -> Result[list[AliasDictEntry]]:
    return PROGRAMM_PARTS.database.select_all(
        table_name=TABLE_ALIAS_NAME, where={FIELD_BOT_ID: bot_id}, type_=AliasDictEntry
    )


def select_dict_entry(bot_id: int, alias: str) -> Result[AliasDictEntry]:
    return PROGRAMM_PARTS.database.select_one(
        table_name=TABLE_ALIAS_NAME, where={FIELD_BOT_ID: bot_id, FIELD_ALIAS_NAME: alias}, type_=AliasDictEntry
    )


def select_dict_entry_by_id(entry_id: int) -> Result[AliasDictEntry]:
    return PROGRAMM_PARTS.database.select_one(
        table_name=TABLE_ALIAS_NAME, where={FIELD_ID: entry_id}, type_=AliasDictEntry
    )


def insert_dict_entry(bot_id: int, alias: str, explanation: str) -> Result[AliasDictEntry]:
    result = PROGRAMM_PARTS.database.insert(
        TABLE_ALIAS_NAME, {FIELD_BOT_ID: bot_id, FIELD_ALIAS_NAME: alias, FIELD_ALIAS_EXPLANATION: explanation}
    )

    if result.state.fail or result.value is None:
        return result.cast_to(AliasDictEntry)

    return select_dict_entry(bot_id, alias)


def update_dict_entry(bot_id: int, alias: str, data: dict[str, Any]) -> Result[AliasDictEntry]:
    result = PROGRAMM_PARTS.database.update(
        TABLE_ALIAS_NAME, where={FIELD_BOT_ID: bot_id, FIELD_ALIAS_NAME: alias}, data=data
    )

    if result.state.fail:
        return result.cast_to(AliasDictEntry)

    lookup_alias = alias
    if FIELD_ALIAS_NAME in data:
        lookup_alias = data[FIELD_ALIAS_NAME]

    return select_dict_entry(bot_id, lookup_alias)


def update_dict_entry_by_id(entry_id: int, data: dict[str, Any]) -> Result[AliasDictEntry]:
    result = PROGRAMM_PARTS.database.update(TABLE_ALIAS_NAME, where={FIELD_ID: entry_id}, data=data)

    if result.state.fail:
        return result.cast_to(AliasDictEntry)

    return select_dict_entry_by_id(entry_id)


def delete_dict_entry(bot_id: int, alias: str) -> Result[None]:
    return PROGRAMM_PARTS.database.delete(TABLE_ALIAS_NAME, where={FIELD_BOT_ID: bot_id, FIELD_ALIAS_NAME: alias})


def delete_dict_entry_by_id(entry_id: int) -> Result[None]:
    return PROGRAMM_PARTS.database.delete(TABLE_ALIAS_NAME, where={FIELD_ID: entry_id})
