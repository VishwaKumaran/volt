from pathlib import Path

from rich import print

from volt.core.dependencies import install_fastapi_dependencies
from volt.core.prompts import choose
from volt.core.template import copy_template, inject_variables_in_file


def create_fastapi_app(name: Path | str, skip_install: bool = False):
    dest = Path(name)
    project_name = dest.name
    if dest.exists():
        print(f"The folder '{name}' already exists.")
        return

    print(f"Creating FastAPI project {project_name} ...")

    db_choice = choose(
        "Select a database:",
        choices=["None", "SQLite", "PostgreSQL", "MySQL"],
    )

    copy_template("fastapi", "base", dest)
    db_block = generate_db_block(db_choice, project_name)

    config_path = Path(dest) / "app" / "core" / "config.py"

    inject_variables_in_file(config_path, {
        "PROJECT_NAME": project_name,
        "DB_BLOCK": db_block
    })

    if not skip_install:
        install_fastapi_dependencies(dest, db_choice)


def generate_db_block(db_choice: str, project_name: str) -> str:
    if db_choice == "SQLite":
        return f'''
    DB_PATH: str = "data/{project_name}.db"

    @computed_field
    @property
    def DATABASE_URI(self) -> str:
        return f"sqlite+aiosqlite:///{{self.DB_PATH}}"
    '''
    elif db_choice == "PostgreSQL":
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
    else:
        return "# No database configured"
