from enum import IntEnum
from typing import Self
from typing import final


@final
class PermissionLevel(IntEnum):
    USER = 10
    SPECIAL_USER = 20
    MODERATOR = 30
    ADMIN = 40

    def is_permitted(self, needed: Self) -> bool:
        return self >= needed
