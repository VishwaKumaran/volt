import re
from pathlib import Path

from rich import print

from volt.core.injectors import replace_pattern_in_file
from volt.stacks.constants import DB_SQL_MODEL


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


def register_model_in_init_beanie(db_file: Path, model_name: str):
    content = db_file.read_text()

    pattern = r"await\s+init_beanie\s*\(\s*database\s*=\s*db\s*,\s*document_models\s*=\s*\[([^\]]*)\]\s*\)"
    match = re.search(pattern, content, flags=re.DOTALL)

    if not match:
        return

    existing_models = match.group(1).strip()
    if existing_models:
        models = [m.strip() for m in existing_models.split(",") if m.strip()]
        if model_name not in models:
            models.append(model_name)
        new_models = ", ".join(models)
    else:
        new_models = model_name

    new_content = re.sub(pattern, f"await init_beanie(database=db, document_models=[{new_models}])", content)
    db_file.write_text(new_content)


def inject_healthcheck_route(main_file: Path, db_choice: str):
    content = main_file.read_text()
    if '@app.get("/health"' in content:
        print("[yellow]Healthcheck route already exists, skipping.[/yellow]")
        return

    if db_choice == "MongoDB":
        import_code = '''from fastapi import HTTPException
from app.core.config import settings
import app.core.db as db'''
        health_code = '''
@app.get("/health", tags=["Health"])
async def healthcheck():
    try:
        if not db.client:
            raise Exception("Database not initialized")
        await db.client.admin.command("ping")
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database not reachable: {e}")
    return {"status": "ok", "database": "reachable"}
'''
    else:
        import_code = '''
        from sqlalchemy import text
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio.session import AsyncSession
from app.core.db import get_session'''
        health_code = '''
@app.get("/health", tags=["Health"])
async def healthcheck(session: AsyncSession = Depends(get_session)):
    try:
        await session.execute(text("SELECT 1"))
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database not reachable: {e}")
    return {"status": "ok", "database": "reachable"}
'''

    if import_code.strip() not in content:
        pattern_import = r"(?:(?:from|import)\s+[^\n]+\n)+"
        match = re.search(pattern_import, content)
        if match:
            insert_pos = match.end()
            content = content[:insert_pos] + "\n" + import_code.strip() + "\n\n" + content[insert_pos:]
        else:
            content = import_code.strip() + "\n\n" + content

    pattern = r"app\.include_router\([^\n]+\)\n"
    new_content = re.sub(pattern, lambda m: m.group(0) + "\n" + health_code.strip() + "\n", content)
    main_file.write_text(new_content)


def inject_auth_routers(routers_file: Path):
    new_router_code = """from fastapi import APIRouter

from app.core.config import settings
from app.routers.auth.router import router as auth_router
from app.routers.users.router import router as user_router

api_router = APIRouter(prefix=settings.API_V1)
api_router.include_router(auth_router)
api_router.include_router(user_router)
"""

    content = routers_file.read_text()

    if "app.routers.auth.router" in content and "app.routers.users.router" in content:
        print("[yellow]Routers already injected, skipping.[/yellow]")
        return

    pattern = (
        r"from fastapi import APIRouter\s+from app\.core\.config import settings\s+"
        r"api_router = APIRouter\(prefix=settings\.API_V1\)"
    )

    replace_pattern_in_file(routers_file, pattern, new_router_code.strip())


def inject_users_model(models_file: Path, db_choice: str):
    if db_choice == "MongoDB":
        register_model_in_init_beanie(models_file.parent.parent / "core" / "db.py", "User")
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
        new_model_code = """from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    disabled = Column(Boolean, default=False)
"""
    else:
        raise ValueError(f"Unsupported database choice: {db_choice}")

    models_file.write_text(new_model_code)
