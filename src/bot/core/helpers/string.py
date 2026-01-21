from bot.core.types.result import Result
from bot.core.types.result import ResultState


def identifier_for_db(string: str) -> str:
    return string.strip().lower()


def strip_for_db(string_id: str) -> str:
    return string_id.strip()


def name_for_db(string: str) -> str:
    return string.strip().title()


def has_whitespace(string: str) -> bool:
    return any(char.isspace() for char in string)


def check_identifier(name: str) -> Result[str]:
    name_id = identifier_for_db(name)
    if not name_id:
        return Result(ResultState.EMPTY_NAME, None)

    if has_whitespace(name_id):
        return Result(ResultState.WHITESPACE_ERROR, None)

    return Result(ResultState.SUCCESS, name_id)


def check_text(text: str) -> Result[str]:
    text_db = strip_for_db(text)
    if not text_db:
        return Result(ResultState.EMPTY_MESSAGE, None)

    return Result(ResultState.SUCCESS, text_db)
