from pathlib import Path

from volt.core.dependencies import install_uv_packages, init_uv_project

STACK_DEPS = ["fastapi", "uvicorn", "pydantic-settings"]
REDIS_DEPS = ["redis"]
TASKIQ_DEPS = ["taskiq", "taskiq-redis"]
SENTRY_DEPS = ["sentry-sdk[fastapi]"]

FASTAPI_DB_DEPS = {
    "sqlite": ["sqlmodel", "aiosqlite", "greenlet", "alembic"],
    "postgresql": ["sqlmodel", "asyncpg", "greenlet", "alembic"],
    "mysql": ["sqlmodel", "aiomysql", "greenlet", "cryptography", "alembic"],
    "mongodb": ["beanie"],
}

FASTAPI_AUTH_DEPS = {
    "Bearer Token (Authorization Header)": [
        "pwdlib[argon2]",
        "pydantic[email]",
        "pyjwt",
        "python-multipart",
    ],
    "Cookie-based Authentication (HTTPOnly)": [
        "pwdlib[argon2]",
        "pydantic[email]",
        "pyjwt",
        "python-multipart",
    ],
}


def install_fastapi_dependencies(
    dest: Path,
    db_choice: str,
    auth_choice: str,
    redis_choice: bool = False,
    taskiq_choice: bool = False,
    sentry_choice: bool = False,
):
    init_uv_project(dest)

    install_uv_packages(STACK_DEPS, dest)

    if redis_choice:
        install_uv_packages(REDIS_DEPS, dest)

    if taskiq_choice:
        install_uv_packages(TASKIQ_DEPS, dest)

    if sentry_choice:
        install_uv_packages(SENTRY_DEPS, dest)

    db_key = db_choice.lower()
    if db_choice != "None" and db_key in FASTAPI_DB_DEPS:
        deps = FASTAPI_DB_DEPS[db_key]
        install_uv_packages(deps, dest)

    if auth_choice != "None" and auth_choice in FASTAPI_AUTH_DEPS:
        deps = FASTAPI_AUTH_DEPS[auth_choice]
        install_uv_packages(deps, dest)
