from bot.core.helpers.string import has_whitespace
from bot.core.helpers.string import identifier_for_db
from bot.core.helpers.string import strip_for_db
from bot.core.types.result import Result
from bot.core.types.result import ResultState
from bot.database.alias_dict import FIELD_ALIAS
from bot.database.alias_dict import FIELD_EXPLANATION
from bot.database.alias_dict import delete_dict_entry as delete_dict_entry_db
from bot.database.alias_dict import insert_dict_entry as insert_dict_entry_db
from bot.database.alias_dict import select_dict_from_bot as select_dict_from_bot_db
from bot.database.alias_dict import update_dict_entry as update_dict_entry_db
from bot.database.types.alias_dict_entry import AliasDictEntry


def select_dict_from_bot(bot_id: int) -> Result[list[AliasDictEntry]]:
    return select_dict_from_bot_db(bot_id)


def alias_lookup(bot_id: int, message: str) -> Result[list[str]]:
    alias_dict = select_dict_from_bot_db(bot_id)

    if alias_dict.state.fail or alias_dict.value is None or len(alias_dict.value) == 0:
        return alias_dict.cast_to(list[str], [])

    lookups: list[str] = []

    for entry in alias_dict.value:
        if entry.alias in message.lower():
            lookups.append(f"{entry.alias}: {entry.explanation}")

    return Result(ResultState.SUCCESS, lookups)


def add_alias(bot_id: int, alias: str, explanation: str) -> Result[AliasDictEntry]:
    alias_db = identifier_for_db(alias)
    explanation_db = strip_for_db(explanation)
    if not alias_db:
        return Result(ResultState.EMPTY_NAME, None)
    if not explanation_db:
        return Result(ResultState.EMPTY_MESSAGE, None)
    if has_whitespace(alias_db):
        return Result(ResultState.WHITESPACE_ERROR, None)

    return insert_dict_entry_db(bot_id, alias_db, explanation_db)


def edit_dict_alias(bot_id: int, old_alias: str, new_alias: str) -> Result[AliasDictEntry]:
    old_alias_db = identifier_for_db(old_alias)
    new_alias_db = identifier_for_db(new_alias)

    if not new_alias_db:
        return Result(ResultState.EMPTY_NAME, None)
    if has_whitespace(new_alias_db):
        return Result(ResultState.WHITESPACE_ERROR, None)

    return update_dict_entry_db(bot_id, old_alias_db, {FIELD_ALIAS: new_alias_db})


def edit_dict_explanation(bot_id: int, alias: str, explanation: str) -> Result[AliasDictEntry]:
    alias_db = identifier_for_db(alias)
    explanation_db = strip_for_db(explanation)

    if not explanation_db:
        return Result(ResultState.EMPTY_MESSAGE, None)

    return update_dict_entry_db(bot_id, alias_db, {FIELD_EXPLANATION: explanation_db})


def delete_alias(bot_id: int, alias: str) -> Result[None]:
    return delete_dict_entry_db(bot_id, identifier_for_db(alias))
