from enum import IntEnum
from typing import Self
from typing import final

from pydantic import BaseModel


@final
class PermissionLevelDTO(BaseModel):
    name: str
    value: int
    display_name: str


@final
class PermissionLevel(IntEnum):
    USER = 10
    SPECIAL_USER = 20
    MODERATOR = 30
    ADMIN = 40

    def is_permitted(self, needed: Self) -> bool:
        return self >= needed

    def to_dto(self) -> PermissionLevelDTO:
        return PermissionLevelDTO(
            name=self.name,
            value=self.value,
            display_name=self.name.replace("_", " ").title(),
        )

    @classmethod
    def get_all_dto(cls) -> list[PermissionLevelDTO]:
        return [permission_level.to_dto() for permission_level in cls]
