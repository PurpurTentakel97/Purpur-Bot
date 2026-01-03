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
