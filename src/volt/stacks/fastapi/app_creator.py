import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

from rich import print

from volt.core.prompts import choose
from volt.stacks.fastapi.dependencies import install_fastapi_dependencies
from volt.stacks.fastapi.helpers import (
    setup_db_templates,
    setup_auth_templates,
)
from volt.stacks.fastapi.template_utils import (
    copy_fastapi_base_template,
    prepare_fastapi_template,
)


def create_fastapi_app(name: Path | str, skip_install: bool = False):
    dest = Path(name)
    project_name = dest.name

    if dest.exists():
        print(f"[red]The folder '{dest.resolve()}' already exists.[/red]")
        return

    try:
        db_choice = choose(
            "Select a database:",
            choices=["None", "SQLite", "PostgreSQL", "MySQL", "MongoDB"],
            default="None",
        )
        auth_choice = choose(
            "Select an authentication method:",
            choices=[
                "None",
                "Bearer Token (Authorization Header)",
                "Cookie-based Authentication (HTTPOnly)",
            ],
            default="None",
        ) if db_choice != "None" else "None"
    except KeyboardInterrupt:
        return

    try:
        with TemporaryDirectory() as tmpdir:
            temp_path = Path(tmpdir)
            copy_fastapi_base_template(temp_path)

            setup_db_templates(temp_path, db_choice)
            setup_auth_templates(temp_path, auth_choice, db_choice)

            prepare_fastapi_template(temp_path, project_name, db_choice, auth_choice)

            shutil.move(str(temp_path), dest)

        if not skip_install:
            install_fastapi_dependencies(dest, db_choice, auth_choice)
    except Exception as e:
        print(f"[red]Error creating FastAPI app: {e}[/red]")
        raise e
        return

    print()
    print(f"[green]✔ Successfully created FastAPI app:[/green] [bold]{project_name}[/bold]")
    print(f"[dim]Location:[/dim] [blue]{dest.resolve()}[/blue]")
    print()
    print("[bold]Next steps:[/bold]")
    print(f"  1. [cyan]cd {project_name}[/cyan]")
    if not skip_install:
        print("  2. [cyan]uv run uvicorn app.main:app[/cyan]")
    else:
        print("  2. [cyan]Install dependencies manually[/cyan]")
