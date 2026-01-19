# Build stage
FROM python:3.14-slim-bookworm AS builder

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-install-project

COPY src/ ./src/

RUN uv sync --frozen

FROM python:3.14-slim-bookworm AS runtime

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY src/ ./src/

ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app/src

FROM runtime AS api

EXPOSE 8000

CMD ["fastapi", "run", "--entrypoint", "entrypoint.api:app"]

FROM runtime AS taskiq

CMD ["taskiq", "worker", "entrypoint.queue:broker"]
