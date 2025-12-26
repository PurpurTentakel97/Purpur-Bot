from pathlib import Path
from typing import Final
from typing import final

from pydantic import BaseModel

from bot.helpers.file import load_json
from bot.helpers.file import save_json
from bot.helpers.log import LogLevel
from bot.helpers.log import log_default

_CONFIG_SAMPLE_FILE: Path = Path("config_sample.json")
_CONFIG_FILE: Path = Path("config.json")


@final
class Config(BaseModel):
    discord_token: str = "<DISCORD_TOKEN>"
    twitch_client_id: str = "<TWITCH_CLIENT_ID>"
    twitch_credentials: str = "<TWITCH_CREDENTIALS>"


def load_config() -> Config:
    sample_result: Final = load_json(_CONFIG_SAMPLE_FILE, Config)
    if not sample_result.success:
        log_default(LogLevel.INFO, f"Not able to load {_CONFIG_SAMPLE_FILE} -> Try to generate a new one....")
        sample_save_result = save_json(_CONFIG_SAMPLE_FILE, Config())
        if not sample_save_result.success:
            log_default(LogLevel.CRITICAL, f"Failed to create a {_CONFIG_SAMPLE_FILE}")
        else:
            log_default(LogLevel.INFO, f"{_CONFIG_SAMPLE_FILE} generated")

    result: Final = load_json(_CONFIG_FILE, Config)
    if result.success and result.data:
        log_default(LogLevel.INFO, f"{_CONFIG_FILE} loaded successfully")
        return result.data

    log_default(LogLevel.CRITICAL, f"Failed to load config {_CONFIG_FILE} -> Will raise")
    raise Exception(f"Failed to load config {_CONFIG_FILE}")
