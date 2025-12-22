from pathlib import Path

from volt.core.template import copy_template
from volt.stacks.constants import DB_NOSQL_MODEL, DB_SQL_MODEL
from volt.stacks.fastapi.injectors import (
    inject_auth_routers,
    inject_users_model,
    inject_healthcheck_route,
    inject_lifespan,
)


def setup_db_templates(dest: Path, db_choice: str):
    from volt.stacks.constants import DB_NOSQL_MODEL
    from volt.stacks.constants import DB_SQL_MODEL

    if db_choice in DB_SQL_MODEL:
        copy_template("fastapi", "db_sqlmodel", dest, True)
    elif db_choice in DB_NOSQL_MODEL:
        copy_template("fastapi", "db_mongo", dest, True)

    if db_choice != "None":
        inject_lifespan(db_choice, dest / "app" / "main.py")
        inject_healthcheck_route(dest / "app" / "main.py", db_choice)


def setup_auth_templates(dest: Path, auth_choice: str, db_choice: str):
    if auth_choice == "None":
        return
    auth_type = "auth_bearer" if "Bearer" in auth_choice else "auth_cookie"
    auth_type_model = f"{auth_type}_model"
    copy_template("fastapi", auth_type, dest, True)

    inject_auth_routers(dest / "app" / "routers" / "main.py")
    inject_users_model(dest / "app" / "models" / "user.py", db_choice)

    if db_choice in DB_NOSQL_MODEL:
        copy_template("fastapi", f"{auth_type_model}/mongo", dest, True)
    elif db_choice in DB_SQL_MODEL:
        copy_template("fastapi", f"{auth_type_model}/sqlmodel", dest, True)


def setup_docker_templates(
    dest: Path,
    db_choice: str,
    redis_choice: bool = False,
    taskiq_choice: bool = False,
):
    from volt.core.template import copy_template
    from volt.stacks.fastapi.docker_config import DOCKER_CONFIGS

    copy_template("fastapi", "docker", dest, True)

    docker_compose_path = dest / "docker-compose.yaml"
    if not docker_compose_path.exists():
        return

    content = docker_compose_path.read_text()

    if db_choice == "SQLite" or db_choice == "None":
        # Remove db service and depends_on
        import re

        content = re.sub(
            r"\s+depends_on:\s+db:\s+condition: service_healthy", "", content
        )
        content = re.sub(r"\s+db:\s+# DB_CONFIG", "", content)
    else:
        db_config = DOCKER_CONFIGS.get(db_choice, "")
        content = content.replace("# DB_CONFIG", db_config.strip())

    if redis_choice or taskiq_choice:
        # TaskIQ needs Redis (in our setup)
        redis_service = """
  redis:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5
"""
        if "redis:" not in content:
            content += redis_service

        # Add to depends_on of app
        if "depends_on:" in content:
            if "redis:" not in content.split("depends_on:")[1].split("services:")[0]:
                content = content.replace(
                    "depends_on:",
                    "depends_on:\n      redis:\n        condition: service_healthy",
                )

    if taskiq_choice:
        worker_service = """
  worker:
    build: .
    command: uv run taskiq worker app.core.tasks:broker
    env_file:
      - .env
    depends_on:
      redis:
        condition: service_healthy
"""
        content += worker_service

    docker_compose_path.write_text(content)


def setup_alembic_templates(dest: Path):
    from volt.core.template import copy_template

    copy_template("fastapi", "alembic", dest, True)


def setup_redis_templates(dest: Path):
    from volt.core.template import copy_template
    from volt.stacks.fastapi.injectors import inject_redis

    copy_template("fastapi", "redis", dest, True)
    inject_redis(dest / "app" / "main.py")


def setup_taskiq_templates(dest: Path):
    from volt.core.template import copy_template
    from volt.stacks.fastapi.injectors import inject_taskiq

    copy_template("fastapi", "taskiq", dest, True)
    inject_taskiq(dest / "app" / "main.py")
