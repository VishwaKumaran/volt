from pathlib import Path

from volt.core.dependencies import install_uv_packages, init_uv_project

STACK_DEPS = ["fastapi", "uvicorn", "pydantic-settings"]

FASTAPI_DB_DEPS = {
    "sqlite": ["sqlmodel", "aiosqlite"],
    "postgresql": ["sqlmodel", "asyncpg"],
    "mysql": ["sqlmodel", "aiomysql"],
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


def install_fastapi_dependencies(dest: Path, db_choice: str, auth_choice: str):
    init_uv_project(dest)

    install_uv_packages(STACK_DEPS, dest)

    db_key = db_choice.lower()
    if db_choice != "None" and db_key in FASTAPI_DB_DEPS:
        deps = FASTAPI_DB_DEPS[db_key]
        install_uv_packages(deps, dest)

    if auth_choice != "None" and auth_choice in FASTAPI_AUTH_DEPS:
        deps = FASTAPI_AUTH_DEPS[auth_choice]
        install_uv_packages(deps, dest)
