from pathlib import Path
from typing import Optional
from typing import final

from pydantic import BaseModel
from pydantic import ValidationError

from bot.helpers.log import LogLevel
from bot.helpers.log import log_default

PATH = Path.cwd() / "config.json"


@final
class UserConfig(BaseModel):
    id: int
    name: str
    twitch: list[str]
    discord: list[int]


@final
class ProgrammConfig(BaseModel):
    version: str = "0.0.1"
    user: list[UserConfig]


def _save_default_config() -> None:
    default_config: ProgrammConfig = ProgrammConfig(
        user=[UserConfig(id=0, name="default", twitch=["twitch_channel_name"], discord=[0])]
    )
    with PATH.open("w") as file:
        file.write(default_config.model_dump_json(indent=2))
        log_default(LogLevel.INFO, "default config saved successfully")


def get_config() -> Optional[ProgrammConfig]:
    if not PATH.exists():
        log_default(LogLevel.INFO, "config.json not found, creating default config")
        _save_default_config()
        log_default(LogLevel.WARNING, "Default config: Try to terminate and edit the config.json file manually")
        return None

    with PATH.open("r") as file:
        try:
            config = ProgrammConfig.model_validate_json(file.read())
        except ValidationError as e:
            log_default(LogLevel.ERROR, f"config.json is invalid: {e}")
            return None
        log_default(LogLevel.INFO, "config loaded successfully")
        return config
