from pathlib import Path

from volt.core.template import (
    copy_template,
    inject_variables_in_file,
    format_with_black,
)
from .config_blocks import generate_db_block, generate_auth_block


def prepare_fastapi_template(
    dest: Path,
    project_name: str,
    db_choice: str,
    auth_choice: str,
    docker: bool = False,
    redis_choice: bool = False,
    taskiq_choice: bool = False,
    sentry_choice: bool = False,
) -> None:
    from .config_blocks import generate_redis_block, generate_sentry_block

    env_path = dest / ".env"
    env_example_path = dest / ".env.example"

    db_block = generate_db_block(
        db_choice, env_path, env_example_path, project_name, docker
    )
    auth_block = generate_auth_block(auth_choice, env_path, env_example_path)
    redis_block = (
        generate_redis_block(env_path, env_example_path, docker) if redis_choice else ""
    )
    sentry_block = (
        generate_sentry_block(env_path, env_example_path) if sentry_choice else ""
    )

    config_path = dest / "app" / "core" / "config.py"
    inject_variables_in_file(
        config_path,
        {
            "PROJECT_NAME": project_name,
            "DB_BLOCK": db_block,
            "AUTH_BLOCK": auth_block,
            "REDIS_BLOCK": redis_block,
            "SENTRY_BLOCK": sentry_block,
        },
    )

    format_with_black(dest)


def copy_fastapi_base_template(dest: Path) -> None:
    copy_template("fastapi", "base", dest, True)


def add_fastapi_subtemplate(dest: Path, category: str, name: str) -> None:
    template_path = f"{category}_{name}"
    copy_template("fastapi", template_path, dest, dirs_exist_ok=True)
