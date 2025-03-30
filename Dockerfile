FROM python:3.13-slim as uv-installer
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project

ADD pyproject.toml uv.lock /app/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

ADD oura_bot/ /app/oura_bot/
ADD tests/ /app/test/
ADD users.toml /app/

CMD ["uv", "run", "python", "-m", "oura_bot.main"]
