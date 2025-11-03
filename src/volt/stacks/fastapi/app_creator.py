from pathlib import Path

from rich import print

from volt.core.prompts import choose
from volt.stacks.fastapi.dependencies import install_fastapi_dependencies
from volt.stacks.fastapi.helpers import (
    setup_db_templates,
    setup_auth_templates,
    announce_creation,
    announce_done,
)
from volt.stacks.fastapi.template_utils import (
    copy_fastapi_base_template,
    prepare_fastapi_template,
)


def create_fastapi_app(name: Path | str, skip_install: bool = False):
    dest = Path(name)
    project_name = dest.name

    if dest.exists():
        print(f"[red]The folder '{name}' already exists.[/red]")
        return

    announce_creation(project_name)

    db_choice = choose(
        "Select a database:",
        choices=["None", "SQLite", "PostgreSQL", "MySQL", "MongoDB"],
    )
    auth_choice = choose(
        "Select an authentication method:",
        choices=[
            "None",
            "Bearer Token (Authorization Header)",
            "Cookie-based Authentication (HTTPOnly)",
        ],
        default="None",
    )

    copy_fastapi_base_template(dest)

    setup_db_templates(dest, db_choice)
    setup_auth_templates(dest, auth_choice, db_choice)

    prepare_fastapi_template(dest, project_name, db_choice, auth_choice)

    if not skip_install:
        install_fastapi_dependencies(dest, db_choice, auth_choice)

    announce_done(project_name)
