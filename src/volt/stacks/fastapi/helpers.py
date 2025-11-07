from pathlib import Path

from volt.core.template import copy_template
from volt.stacks.fastapi.injectors import inject_lifespan_for_mongo, inject_auth_routers, inject_users_model


def setup_db_templates(dest: Path, db_choice: str):
    from volt.stacks.constants import DB_NOSQL_MODEL
    from volt.stacks.constants import DB_SQL_MODEL

    if db_choice in DB_SQL_MODEL:
        copy_template("fastapi", "db_sqlmodel", dest, True)
    elif db_choice in DB_NOSQL_MODEL:
        copy_template("fastapi", "db_mongo", dest, True)
        inject_lifespan_for_mongo(dest / "app" / "main.py")


def setup_auth_templates(dest: Path, auth_choice: str, db_choice: str):
    if auth_choice == "None":
        return
    auth_type = "auth_bearer" if "Bearer" in auth_choice else "auth_cookie"
    copy_template("fastapi", auth_type, dest, True)

    inject_auth_routers(dest / "app" / "routers" / "main.py")
    inject_users_model(dest / "app" / "models" / "user.py", db_choice)
