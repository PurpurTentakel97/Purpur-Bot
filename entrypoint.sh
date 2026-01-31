#!/usr/bin/env sh
uv run --no-dev alembic upgrade head
uv run --no-dev uvicorn --host 0.0.0.0 --port 8000 bot.main:app
