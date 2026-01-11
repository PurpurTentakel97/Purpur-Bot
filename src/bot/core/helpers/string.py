def identifier_for_db(string: str) -> str:
    return string.strip().lower()


def strip_for_db(string_id: str) -> str:
    return string_id.strip()


def name_for_db(string: str) -> str:
    return string.strip().title()


def has_whitespace(string: str) -> bool:
    return any(char.isspace() for char in string)
