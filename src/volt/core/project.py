from pathlib import Path

from volt.core.dependencies import install_dependencies
from volt.core.template import copy_template, inject_variables


def create_project(name: str, stack: str, skip_install: bool = False):
    dest = Path(name)
    if dest.exists():
        print(f"The folder '{name}' already exists.")
        return

    print(f"Creating project {name} with {stack} template...")
    copy_template(stack, "base", dest)
    inject_variables(dest, {"PROJECT_NAME": name})

    if not skip_install:
        install_dependencies(dest, stack)

    if stack == "fastapi":
        print(f"To start: cd {name} && uv run uvicorn app.main:app --reload")
