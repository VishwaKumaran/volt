import re
from pathlib import Path

from rich import print

from volt.core.injectors import replace_pattern_in_file
from volt.stacks.constants import DB_SQL_MODEL, DB_NOSQL_MODEL


def inject_lifespan_for_mongo(main_file: Path):
    content = main_file.read_text()
    if "lifespan=" in content:
        return

    pattern = r"app\s*=\s*FastAPI\s*\(([^)]*)\)"
    match = re.search(pattern, content)
    if not match:
        raise RuntimeError("FastAPI app instance not found in main.py")

    lifespan_code = """\n
from contextlib import asynccontextmanager
from app.core.db import init_db, close_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()
"""

    new_content = re.sub(
        pattern,
        f"{lifespan_code}\napp = FastAPI(\\1, lifespan=lifespan)",
        content,
    )
    main_file.write_text(new_content)


def inject_lifespan_for_sqlmodel(main_file: Path):
    content = main_file.read_text()
    if "lifespan=" in content:
        return

    pattern = r"app\s*=\s*FastAPI\s*\(([^)]*)\)"
    match = re.search(pattern, content)
    if not match:
        raise RuntimeError("FastAPI app instance not found in main.py")

    lifespan_code = """\n
from contextlib import asynccontextmanager
from app.core.db import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
"""

    new_content = re.sub(
        pattern,
        f"{lifespan_code}\napp = FastAPI(\\1, lifespan=lifespan)",
        content,
    )
    main_file.write_text(new_content)


def inject_lifespan(db_choice: str, main_file: Path):
    if db_choice in DB_NOSQL_MODEL:
        inject_lifespan_for_mongo(main_file)
    elif db_choice in DB_SQL_MODEL:
        inject_lifespan_for_sqlmodel(main_file)
    else:
        raise ValueError(f"Unsupported database choice: {db_choice}")


def register_model_in_init_beanie(db_file: Path, model_name: str):
    content = db_file.read_text()

    import_stmt = (
        f"from app.models.{model_name.lower()} import {model_name.capitalize()}"
    )

    if import_stmt not in content:
        content = re.sub(
            r"^(from .+|import .+)$",
            r"\1\n" + import_stmt,
            content,
            count=1,
            flags=re.MULTILINE,
        )

    pattern = r"await\s+init_beanie\s*\(\s*database\s*=\s*db\s*,\s*document_models\s*=\s*\[([^\]]*)\]\s*\)"
    match = re.search(pattern, content, flags=re.DOTALL)

    if not match:
        db_file.write_text(content)
        return

    existing_models = match.group(1).strip()
    if existing_models:
        models = [m.strip() for m in existing_models.split(",") if m.strip()]
        if model_name not in models:
            models.append(model_name)
        new_models = ", ".join(models)
    else:
        new_models = model_name

    new_content = re.sub(
        pattern,
        f"await init_beanie(database=db, document_models=[{new_models}])",
        content,
    )
    db_file.write_text(new_content)


def inject_healthcheck_route(main_file: Path, db_choice: str):
    content = main_file.read_text()
    if '@app.get("/health"' in content:
        print("[yellow]Healthcheck route already exists, skipping.[/yellow]")
        return

    if db_choice == "MongoDB":
        import_code = """from fastapi import HTTPException
from app.core.config import settings
import app.core.db as db"""
        health_code = """
@app.get("/health", tags=["Health"])
async def healthcheck():
    try:
        if not db.client:
            raise Exception("Database not initialized")
        await db.client.admin.command("ping")
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database not reachable: {e}")
    return {"status": "ok", "database": "reachable"}
"""
    else:
        import_code = """
        from sqlalchemy import text
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio.session import AsyncSession
from app.core.db import get_session"""
        health_code = """
@app.get("/health", tags=["Health"])
async def healthcheck(session: AsyncSession = Depends(get_session)):
    try:
        await session.execute(text("SELECT 1"))
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database not reachable: {e}")
    return {"status": "ok", "database": "reachable"}
"""

    if import_code.strip() not in content:
        pattern_import = r"(?:(?:from|import)\s+[^\n]+\n)+"
        match = re.search(pattern_import, content)
        if match:
            insert_pos = match.end()
            content = (
                content[:insert_pos]
                + "\n"
                + import_code.strip()
                + "\n\n"
                + content[insert_pos:]
            )
        else:
            content = import_code.strip() + "\n\n" + content

    pattern = r"app\.include_router\([^\n]+\)\n"
    new_content = re.sub(
        pattern, lambda m: m.group(0) + "\n" + health_code.strip() + "\n", content
    )
    main_file.write_text(new_content)


def inject_auth_routers(routers_file: Path):
    new_router_code = """from fastapi import APIRouter

from app.core.config import settings
from app.routers.auth.router import router as auth_router
from app.routers.users.router import router as user_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(user_router)
"""

    content = routers_file.read_text()

    if "app.routers.auth.router" in content and "app.routers.users.router" in content:
        print("[yellow]Routers already injected, skipping.[/yellow]")
        return

    pattern = (
        r"from fastapi import APIRouter\s+from app\.core\.config import settings\s+"
        r"api_router = APIRouter\(\)"
    )

    replace_pattern_in_file(routers_file, pattern, new_router_code.strip())


def inject_users_model(models_file: Path, db_choice: str):
    if db_choice == "MongoDB":
        register_model_in_init_beanie(
            models_file.parent.parent / "core" / "db.py", "User"
        )
        new_model_code = """from beanie import Document
from pydantic import EmailStr


class User(Document):
    username: str
    email: EmailStr
    hashed_password: str
    disabled: bool = False

    class Settings:
        name = "users"
"""
    elif db_choice in DB_SQL_MODEL:
        new_model_code = """from typing import Optional

from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, nullable=False, unique=True)
    email: str = Field(index=True, nullable=False, unique=True)
    hashed_password: str
    disabled: bool = False
"""
    else:
        raise ValueError(f"Unsupported database choice: {db_choice}")


def inject_redis(main_file: Path):
    content = main_file.read_text()
    if "init_redis" in content:
        return

    import_code = "from app.core.redis import init_redis, close_redis"
    if import_code not in content:
        # Add after other app imports
        content = re.sub(
            r"(from app\.core\.db import [^\n]+)", r"\1\n" + import_code, content
        )

    # Inject into lifespan
    if "async def lifespan(app: FastAPI):" in content:
        content = re.sub(r"(await init_db\(\))", r"\1\n    await init_redis()", content)
        content = re.sub(
            r"(await close_db\(\))", r"\1\n    await close_redis()", content
        )
    else:
        # Create lifespan if not exists
        lifespan_code = """
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_redis()
    yield
    await close_redis()
"""
        pattern = r"app\s*=\s*FastAPI\s*\(([^)]*)\)"
        content = re.sub(
            pattern,
            f"{lifespan_code}\napp = FastAPI(\\1, lifespan=lifespan)",
            content,
        )


def inject_taskiq(main_file: Path):
    content = main_file.read_text()
    if "broker.startup" in content:
        return

    import_code = "from app.core.tasks import broker"
    if import_code not in content:
        content = re.sub(
            r"(from app\.core\.\w+ import [^\n]+)",
            r"\1\n" + import_code,
            content,
            count=1,
        )

    # Inject into lifespan
    if "async def lifespan(app: FastAPI):" in content:
        content = re.sub(
            r"(await init_redis\(\))", r"\1\n    await broker.startup()", content
        )
        # If no init_redis, try after init_db
        if "await broker.startup()" not in content:
            content = re.sub(
                r"(await init_db\(\))", r"\1\n    await broker.startup()", content
            )

        content = re.sub(
            r"(await close_redis\(\))", r"\1\n    await broker.shutdown()", content
        )
        if "await broker.shutdown()" not in content:
            content = re.sub(
                r"(await close_db\(\))", r"\1\n    await broker.shutdown()", content
            )
    else:
        # Create lifespan if not exists (unlikely given previous steps but for robustness)
        lifespan_code = """
@asynccontextmanager
async def lifespan(app: FastAPI):
    await broker.startup()
    yield
    await broker.shutdown()
"""
        pattern = r"app\s*=\s*FastAPI\s*\(([^)]*)\)"
        content = re.sub(
            pattern,
            f"{lifespan_code}\napp = FastAPI(\\1, lifespan=lifespan)",
            content,
        )


def inject_sentry(main_file: Path):
    content = main_file.read_text()
    if "sentry_sdk.init" in content:
        return

    import_code = """import sentry_sdk
from app.core.config import settings"""

    init_code = """
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
        send_default_pii=True,
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
    )
"""

    if "import sentry_sdk" not in content:
        content = import_code + "\n" + content

    # Inject after app = FastAPI(...)
    pattern = r"(app\s*=\s*FastAPI\s*\([^)]*\))"
    content = re.sub(pattern, r"\1\n" + init_code, content)

    main_file.write_text(content)
