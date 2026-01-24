from typing import Any

from bot.core.types.programm_parts import PROGRAMM_PARTS
from bot.core.types.result import Result
from bot.database.types.alias_dict_entry import AliasDictEntry

TABLE_NAME = "alias_dict"
FIELD_ALIAS = "alias"
FIELD_EXPLANATION = "explanation"
FIELD_ENABLED = "enabled"


def select_dict_from_bot(bot_id: int) -> Result[list[AliasDictEntry]]:
    return PROGRAMM_PARTS.database.select_all(table_name=TABLE_NAME, where={"bot_id": bot_id}, type_=AliasDictEntry)


def select_dict_entry(bot_id: int, alias: str) -> Result[AliasDictEntry]:
    return PROGRAMM_PARTS.database.select_one(
        table_name=TABLE_NAME, where={"bot_id": bot_id, "alias": alias}, type_=AliasDictEntry
    )


def select_dict_entry_by_id(entry_id: int) -> Result[AliasDictEntry]:
    return PROGRAMM_PARTS.database.select_one(table_name=TABLE_NAME, where={"id": entry_id}, type_=AliasDictEntry)


def insert_dict_entry(bot_id: int, alias: str, explanation: str) -> Result[AliasDictEntry]:
    result = PROGRAMM_PARTS.database.insert(TABLE_NAME, {"bot_id": bot_id, "alias": alias, "explanation": explanation})

    if result.state.fail or result.value is None:
        return result.cast_to(AliasDictEntry)

    return select_dict_entry(bot_id, alias)


def update_dict_entry(bot_id: int, alias: str, data: dict[str, Any]) -> Result[AliasDictEntry]:
    result = PROGRAMM_PARTS.database.update(TABLE_NAME, where={"bot_id": bot_id, "alias": alias}, data=data)

    if result.state.fail:
        return result.cast_to(AliasDictEntry)

    lookup_alias = alias
    if FIELD_ALIAS in data:
        lookup_alias = data[FIELD_ALIAS]

    return select_dict_entry(bot_id, lookup_alias)


def update_dict_entry_by_id(entry_id: int, data: dict[str, Any]) -> Result[AliasDictEntry]:
    result = PROGRAMM_PARTS.database.update(TABLE_NAME, where={"id": entry_id}, data=data)

    if result.state.fail:
        return result.cast_to(AliasDictEntry)

    return select_dict_entry_by_id(entry_id)


def delete_dict_entry(bot_id: int, alias: str) -> Result[None]:
    return PROGRAMM_PARTS.database.delete(TABLE_NAME, where={"bot_id": bot_id, "alias": alias})


def delete_dict_entry_by_id(entry_id: int) -> Result[None]:
    return PROGRAMM_PARTS.database.delete(TABLE_NAME, where={"id": entry_id})
