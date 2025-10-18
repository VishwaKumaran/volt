import subprocess
from pathlib import Path

STACK_DEPS = {
    "fastapi": ["fastapi", "uvicorn", "pydantic-settings"],
}


def install_dependencies(dest: Path, stack: str):
    print(f"Installing dependencies for {stack} ...")
    if stack == "fastapi":
        subprocess.run(["uv", "init"], cwd=dest)
        subprocess.run(["uv", "add", *STACK_DEPS[stack]], cwd=dest)
