"""Pytest configuration and fixtures for all tests."""

import os

# Set environment variables before any imports that might load `CONFIG`.
# This must happen at module level, before pytest collection, because
# otherwise loading the `CONFIG` variable fails if the environment variables
# are not set (e.g., in CI environments, where the `.env` file does not
# exist).
os.environ.setdefault("DISCORD_TOKEN", "DISCORD_TOKEN")
os.environ.setdefault("TWITCH_CLIENT_ID", "TWITCH_CLIENT_ID")
os.environ.setdefault("TWITCH_CREDENTIALS", "TWITCH_CREDENTIALS")
os.environ.setdefault("JWT_SECRET", "JWT_SECRET")
os.environ.setdefault("TWITCH_LIVE_MESSAGE_COOLDOWN_IN_SECONDS", "7200")
os.environ.setdefault("COMMAND_RESPONSE_COOLDOWN_IN_SECONDS", "15")
os.environ.setdefault("ALIAS_RESPONSE_COOLDOWN_IN_SECONDS", "15")
os.environ.setdefault("QUOTE_RESPONSE_COOLDOWN_IN_SECONDS", "3600")

import pytest  # noqa: E402

from bot.core.types.cooldown import CooldownsWrapper  # noqa: E402
from bot.core.types.programm_parts import PROGRAMM_PARTS  # noqa: E402


@pytest.fixture(autouse=True)
def _fresh_quote_cooldown() -> None:  # pyright: ignore [reportUnusedFunction]
    if PROGRAMM_PARTS.cooldowns_unwrapped() is None:
        PROGRAMM_PARTS.cooldowns = CooldownsWrapper()
    PROGRAMM_PARTS.cooldowns.quote_response_cooldown.data.clear()
