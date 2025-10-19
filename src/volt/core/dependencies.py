import subprocess
from pathlib import Path

from rich import print

STACK_DEPS = {
    "fastapi": ["fastapi", "uvicorn", "pydantic-settings"],
}

FASTAPI_DEPS = {
    "sqlite": ["sqlmodel", "aiosqlite"],
    "postgresql": ["sqlmodel", "asyncpg"],
    "mysql": ["sqlmodel", "aiomysql"],
}


def install_fastapi_dependencies(dest: Path, db_choice: str):
    print(f"Installing dependencies for FastAPI project...")
    subprocess.run(["uv", "init"], cwd=dest, check=True)
    subprocess.run(["uv", "add", *STACK_DEPS["fastapi"]], cwd=dest)

    if db_choice != "None":
        subprocess.run(["uv", "add", *FASTAPI_DEPS[db_choice.lower()]], cwd=dest, check=True)
