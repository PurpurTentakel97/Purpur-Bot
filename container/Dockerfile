FROM python:3.12-slim

RUN pip install uv

WORKDIR /app

COPY pyproject.toml /app/
COPY uv.lock /app/
COPY README.md /app/
COPY src /app/src/

RUN uv sync --no-dev --frozen

COPY container/entrypoint.sh /app/
RUN chmod +x /app/*.sh

ENTRYPOINT ["/app/entrypoint.sh"]
