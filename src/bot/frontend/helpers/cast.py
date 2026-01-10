from typing import Optional

from fastapi import HTTPException


def to_int(value: str) -> Optional[int]:
    try:
        return int(value)
    except ValueError:
        return None


def to_int_or_raise(value: str) -> int:
    result = to_int(value)

    if not result:
        raise HTTPException(status_code=400, detail="Invalid int value")

    return result
