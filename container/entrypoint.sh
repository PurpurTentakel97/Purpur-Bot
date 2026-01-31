#!/usr/bin/env sh
uv run --no-dev uvicorn --host 0.0.0.0 --port 8080 bot.main:app
# uv run --no-dev src/bot/main.py
# python src/bot/main.py
sleep 1d
