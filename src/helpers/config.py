from collections.abc import Callable
from dataclasses import dataclass
from dataclasses import fields
from pathlib import Path
from typing import Any
from typing import Self
from typing import final

from src.helpers.file import LoadJsonResult
from src.helpers.file import SaveJsonResult
from src.helpers.file import load_json
from src.helpers.file import save_json
from src.helpers.log import LogLevel
from src.helpers.log import log_default
from src.helpers.my_types import JsonDict

_CONFIG_SAMPLE_FILE: str = "config_sample.json"
_CONFIG_FILE: str = "config.json"


@final
@dataclass(frozen=True)
class Config:
    discord_token: str
    twitch_client_id: str
    twitch_credentials: str

    @classmethod
    def from_dict(cls, data: JsonDict) -> Self:
        field_types: dict[str, Callable[[Any], Any]] = {
            f.name: f.type if callable(f.type) else str for f in fields(cls)
        }

        filtered_data: dict[str, Any] = {key: field_types[key](data[key]) for key in field_types if key in data}
        return cls(**filtered_data)

    @classmethod
    def get_fields(cls) -> list[str]:
        return [f.name for f in fields(cls)]


def _gen_default_config() -> JsonDict:
    config: JsonDict = {}
    for field in Config.get_fields():
        config[field] = f"{field.upper()}"
    return config


def load_config() -> Config:
    def _check_single_field(config: JsonDict, key: str) -> bool:
        if key not in config:
            log_default(LogLevel.ERROR, f"Config file does not contain required key {key}")
            return False

        if config[key] == key.upper():
            log_default(LogLevel.ERROR, f"Config entry {key} has default value {key.upper()}")
            return False

        if config[key] == "":
            log_default(LogLevel.ERROR, f"Config entry {key} is empty")

        return True

    config_sample_result: LoadJsonResult = load_json(Path.cwd() / _CONFIG_SAMPLE_FILE)
    if not config_sample_result.success:
        log_default(LogLevel.INFO, "Config sample file does not exist, creating it...")
        result: SaveJsonResult = save_json(Path.cwd() / _CONFIG_SAMPLE_FILE, _gen_default_config())
        if not result.success:
            log_default(LogLevel.CRITICAL, "Failed to create a config sample file")
            raise Exception("Failed to create a config sample file")

    config_result: LoadJsonResult = load_json(Path.cwd() / _CONFIG_FILE)
    if not config_result.success:
        log_default(LogLevel.CRITICAL, "Failed to load the config file")
        raise Exception("Failed to load the config file")

    valid_data: bool = True
    for key in Config.get_fields():
        valid_data = valid_data and _check_single_field(config_result.data, key)

    if not valid_data:
        log_default(LogLevel.CRITICAL, "Invalid data in config file")
        raise Exception("Invalid data in config file")

    log_default(LogLevel.INFO, "Config file loaded")
    return Config.from_dict(config_result.data)
