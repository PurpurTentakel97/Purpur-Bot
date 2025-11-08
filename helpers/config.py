import json
from pathlib import Path
from typing import Dict

from helpers.log import log, LogLevel


class Config:
    def __init__(self, *, discord_token: str, twitch_client_id: str, twitch_credentials: str):
        self._discord_token: str = discord_token
        self._twitch_client_id: str = twitch_client_id
        self._twitch_credentials: str = twitch_credentials

    @property
    def discord_token(self) -> str:
        return self._discord_token

    @property
    def twitch_client_id(self) -> str:
        return self._twitch_client_id

    @property
    def twitch_credentials(self) -> str:
        return self._twitch_credentials


def load_config() -> Config:
    def load_single_config(path: Path) -> Dict[str, str] | None:
        if not path.exists():
            log(LogLevel.ERROR, f"Config file {path} does not exist")
            return None

        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            log(LogLevel.ERROR, f"Failed to parse config file {path}: {e}")
            return None
        except IOError as e:
            log(LogLevel.ERROR, f"Failed to read config file {path}: {e}")
            return None

    def check_single_config_entry(config: Dict[str, str], config_sample: Dict[str, str], key: str) -> bool:
        if not key in config:
            log(LogLevel.ERROR, f"Config file does not contain required key {key}")
            return False
        if not key in config_sample:
            log(LogLevel.ERROR, f"Config sample file does not contain required key {key}")
            return False
        if config[key] == config_sample[key]:
            log(LogLevel.ERROR, f"Config file key {key} is equal to config sample file key {key}")
            return False
        if config[key] == "":
            log(LogLevel.ERROR, f"Config file key {key} is empty")
        return True

    config: Dict[str, str] | None = load_single_config(Path.cwd() / "config.json")
    config_sample: Dict[str, str] | None = load_single_config(Path.cwd() / "config_sample.json")

    if config is None or config_sample is None:
        log(LogLevel.CRITICAL, "Failed to load config")
        raise Exception("Failed to load config")

    if not check_single_config_entry(config,
                                     config_sample,
                                     "discord_token"):
        raise Exception("Faulty Discord Token")

    if not check_single_config_entry(config,
                                     config_sample,
                                     "twitch_client_id"):
        raise Exception("Faulty Twitch Client ID")

    if not check_single_config_entry(config,
                                     config_sample,
                                     "twitch_credentials"):
        raise Exception("Faulty Twitch Credentials")

    return Config(discord_token=config["discord_token"],
                  twitch_client_id=config["twitch_client_id"],
                  twitch_credentials=config["twitch_credentials"])
