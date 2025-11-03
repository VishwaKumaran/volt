from pathlib import Path

from rich import print

from volt.core.template import copy_template, inject_variables_in_file, format_with_black
from .config_blocks import generate_db_block, generate_auth_block


def prepare_fastapi_template(
        dest: Path,
        project_name: str,
        db_choice: str,
        auth_choice: str,
) -> None:
    print(f"[cyan]Preparing FastAPI template for '{project_name}'...[/cyan]")

    env_path = dest / ".env"
    env_example_path = dest / ".env.example"

    db_block = generate_db_block(db_choice, env_path, env_example_path, project_name)
    auth_block = generate_auth_block(auth_choice, env_path, env_example_path)

    config_path = dest / "app" / "core" / "config.py"
    inject_variables_in_file(
        config_path,
        {
            "PROJECT_NAME": project_name,
            "DB_BLOCK": db_block,
            "AUTH_BLOCK": auth_block,
        },
    )

    format_with_black(dest)

    print(f"[green]✅ FastAPI template ready at:[/green] {dest}")


def copy_fastapi_base_template(dest: Path) -> None:
    copy_template("fastapi", "base", dest)
    print(f"[green]✅ Base FastAPI template copied to:[/green] {dest}")


def add_fastapi_subtemplate(dest: Path, category: str, name: str) -> None:
    template_path = f"{category}_{name}"
    copy_template("fastapi", template_path, dest, dirs_exist_ok=True)
    print(f"[green]✅ Added FastAPI {category} template:[/green] {name}")
