from enum import IntEnum
from typing import final


@final
class PermissionLevel(IntEnum):
    USER = 10
    SPECIAL_USER = 20
    MODERATOR = 30
    ADMIN = 40
