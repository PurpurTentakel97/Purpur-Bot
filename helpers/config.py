from dataclasses import fields, dataclass
from pathlib import Path
from typing import Dict, Self, final

from helpers.file import LoadJsonResult, SaveJsonResult, load_json, save_json
from helpers.log import log, LogLevel

_CONFIG_SAMPLE_FILE: str = "config_sample.json"
_CONFIG_FILE: str = "config.json"


@final
@dataclass(frozen=True)
class Config:
    discord_token: str
    twitch_client_id: str
    twitch_credentials: str

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> Self:
        filtered_data: Dict[str, str] = {key: data[key].strip() for key in Config.get_fields()}
        return cls(**filtered_data)

    @classmethod
    def get_fields(cls) -> list[str]:
        return [f.name for f in fields(cls)]


def _gen_default_config() -> Dict[str, str]:
    config: Dict[str, str] = {}
    for field in Config.get_fields():
        config[field] = f"{field.upper()}"
    return config


def load_config() -> Config:
    def _check_single_field(config: Dict[str, str], key: str) -> bool:
        if not key in config:
            log(LogLevel.ERROR, f"Config file does not contain required key {key}")
            return False

        if config[key].strip() == key.upper():
            log(LogLevel.ERROR, f"Config entry {key} has default value {key.upper()}")
            return False

        if config[key].strip() == "":
            log(LogLevel.ERROR, f"Config entry {key} is empty")

        return True

    config_sample_result: LoadJsonResult = load_json(Path.cwd() / _CONFIG_SAMPLE_FILE)
    if not config_sample_result.success:
        log(LogLevel.INFO, "Config sample file does not exist, creating it")
        result: SaveJsonResult = save_json(Path.cwd() / _CONFIG_SAMPLE_FILE, _gen_default_config())
        if not result.success:
            log(LogLevel.CRITICAL, "Failed to create a config sample file")
            raise Exception("Failed to create a config sample file")

    config_result: LoadJsonResult = load_json(Path.cwd() / _CONFIG_FILE)
    if not config_result.success:
        log(LogLevel.CRITICAL, "Failed to load the config file")
        raise Exception("Failed to load the config file")

    valid_data: bool = True
    for key in Config.get_fields():
        valid_data = valid_data and _check_single_field(config_result.data, key)

    if not valid_data:
        log(LogLevel.CRITICAL, "Invalid data in config file")
        raise Exception("Invalid data in config file")

    return Config.from_dict(config_result.data)
