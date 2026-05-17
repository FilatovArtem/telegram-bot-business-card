# syntax=docker/dockerfile:1.7

# ---- Builder stage ----
FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /uvx /usr/local/bin/

WORKDIR /build

# Cache deps separately from app code
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# Copy app and finalize venv
COPY bot ./bot
COPY migrations ./migrations
COPY alembic.ini ./
COPY data ./data
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# ---- Runtime stage ----
FROM python:3.12-slim

# Non-root user
RUN groupadd --system --gid 1000 bot && \
    useradd --system --uid 1000 --gid bot --create-home --shell /bin/bash bot

WORKDIR /app

COPY --from=builder --chown=bot:bot /build/.venv /app/.venv
COPY --from=builder --chown=bot:bot /build/bot /app/bot
COPY --from=builder --chown=bot:bot /build/migrations /app/migrations
COPY --from=builder --chown=bot:bot /build/alembic.ini /app/alembic.ini
COPY --from=builder --chown=bot:bot /build/data /app/data

RUN mkdir -p /app/data && chown -R bot:bot /app/data

USER bot

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# No HEALTHCHECK: long-polling bot has no HTTP endpoint and slim image lacks pgrep
# (procps install requires apt access, blocked in some sandboxed networks).
# Bot reliability is covered by `restart: unless-stopped` in docker-compose.

CMD ["python", "-m", "bot"]
