FASTAPI_DOCKERFILE = """FROM ghcr.io/astral-sh/uv:python{python_version}-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev
ADD . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

FROM python:{python_version}-slim-bookworm

COPY --from=builder --chown=app:app /app /app
WORKDIR /app

ENV PATH="/app/.venv/bin:$PATH"

CMD ["uvicorn", "--host", "0.0.0.0", "--port", "8000", "app.main:app"]
"""


def generate_docker_compose_string(
    db_choice: str,
    redis_enabled: bool = False,
) -> str:
    from volt.stacks.fastapi.docker_config import DOCKER_CONFIGS

    content = """services:
  app:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
"""

    if db_choice not in ["SQLite", "None"]:
        content += """    depends_on:
      db:
        condition: service_healthy
"""

    if db_choice != "SQLite" and db_choice != "None":
        db_config = DOCKER_CONFIGS.get(db_choice, "").strip()
        content += f"\n  db:\n{db_config.replace('    ', '    ')}\n"

    if redis_enabled:
        redis_service = """
  redis:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5
"""
        content += redis_service

        # Add to depends_on of app
        if "depends_on:" not in content:
            content = content.replace(
                "    env_file:\n      - .env",
                "    env_file:\n      - .env\n    depends_on:\n      redis:\n        condition: service_healthy",
            )
        else:
            content = content.replace(
                "    depends_on:",
                "    depends_on:\n      redis:\n        condition: service_healthy",
            )

    return content
