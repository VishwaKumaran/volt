from pathlib import Path

from rich import print

from volt.core.dependencies import install_fastapi_dependencies
from volt.core.injectors import inject_lifespan_for_mongo, inject_auth_routers, inject_users_model
from volt.core.prompts import choose
from volt.core.template import copy_template, inject_variables_in_file, add_env_variables, format_with_black

DB_SQL_MODEL = ["SQLite", "PostgreSQL", "MySQL"]
DB_NOSQL_MODEL = ["MongoDB"]


def create_fastapi_app(name: Path | str, skip_install: bool = False):
    dest = Path(name)
    project_name = dest.name
    if dest.exists():
        print(f"The folder '{name}' already exists.")
        return

    print(f"Creating FastAPI project {project_name} ...")

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

    copy_template("fastapi", "base", dest)
    env_path = dest / ".env.example"
    db_block = generate_db_block(db_choice, env_path)
    auth_block = generate_auth_block(auth_choice)

    if db_choice in DB_SQL_MODEL:
        copy_template("fastapi", "db_sqlmodel", dest, True)
    elif db_choice in DB_NOSQL_MODEL:
        copy_template("fastapi", "db_mongo", dest, True)
        inject_lifespan_for_mongo(dest / "app" / "main.py")

    if auth_choice == "Bearer Token (Authorization Header)":
        copy_template("fastapi", "auth_bearer", dest, True)
    elif auth_choice == "Cookie-based Authentication (HTTPOnly)":
        copy_template("fastapi", "auth_cookie", dest, True)

    if auth_choice != "None":
        inject_auth_routers(dest / "app" / "routers" / "main.py")
        inject_users_model(dest / "app" / "models" / "user.py", db_choice)

    config_path = Path(dest) / "app" / "core" / "config.py"

    inject_variables_in_file(config_path, {
        "PROJECT_NAME": project_name,
        "DB_BLOCK": db_block,
        "AUTH_BLOCK": auth_block,
    })

    if not skip_install:
        install_fastapi_dependencies(dest, db_choice, auth_choice)

    format_with_black(dest)


def generate_db_block(db_choice: str, env_path: Path) -> str:
    if db_choice == "SQLite":
        add_env_variables(env_path, {
            "DB_PATH": None
        })
        return f'''
    DB_PATH: str

    @computed_field
    @property
    def DATABASE_URI(self) -> str:
        return f"sqlite+aiosqlite:///{{self.DB_PATH}}"
    '''
    elif db_choice == "PostgreSQL":
        add_env_variables(env_path, {
            "DB_HOST": None,
            "DB_PORT": 5432,
            "DB_USER": None,
            "DB_PASSWORD": None,
            "DB_NAME": None,
        })
        return f'''
    DB_HOST: str
    DB_PORT: int = 5432
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    @computed_field
    @property
    def DATABASE_URI(self) -> str:
        return f"postgresql+asyncpg://{{self.DB_USER}}:{{self.DB_PASSWORD}}@{{self.DB_HOST}}:{{self.DB_PORT}}/{{self.DB_NAME}}"
    '''
    elif db_choice == "MySQL":
        add_env_variables(env_path, {
            "DB_HOST": None,
            "DB_PORT": 3306,
            "DB_USER": None,
            "DB_PASSWORD": None,
            "DB_NAME": None,
        })
        return f'''
    DB_HOST: str
    DB_PORT: int = 3306
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    @computed_field
    @property
    def DATABASE_URI(self) -> str:
        return f"mysql+aiomysql://{{self.DB_USER}}:{{self.DB_PASSWORD}}@{{self.DB_HOST}}:{{self.DB_PORT}}/{{self.DB_NAME}}"
    '''
    elif db_choice == "MongoDB":
        add_env_variables(env_path, {
            "DB_HOST": "localhost",
            "DB_PORT": "27017",
            "DB_USER": "",
            "DB_PASSWORD": "",
            "DB_NAME": "app_db",
        })

        return f'''
    DB_HOST: str
    DB_PORT: int = 27017
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    @computed_field
    @property
    def DATABASE_URI(self) -> str:
        if self.DB_USER and self.DB_PASSWORD:
            return f"mongodb://{{self.DB_USER}}:{{self.DB_PASSWORD}}@{{self.DB_HOST}}:{{self.DB_PORT}}/{{self.DB_NAME}}"
        return f"mongodb://{{self.DB_HOST}}:{{self.DB_PORT}}/{{self.DB_NAME}}"
    '''
    else:
        return "\n# No database configured"


def generate_auth_block(auth_choice: str) -> str:
    if auth_choice in ["Bearer Token (Authorization Header)", "Cookie-based Authentication (HTTPOnly)"]:
        return f'''
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
        '''
    else:
        return "\n# No authentication configured"
