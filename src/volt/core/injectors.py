import re
from pathlib import Path

from volt.stacks import DB_SQL_MODEL


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

    pattern = re.compile(
        r"from fastapi import APIRouter\s+from app\.core\.config import settings\s+api_router = APIRouter\(prefix=settings\.API_V1\)",
        re.DOTALL,
    )

    if "app.routers.auth.router" in content and "app.routers.users.router" in content:
        print("Routers already injected.")
        return

    new_content = re.sub(pattern, new_router_code.strip(), content)

    routers_file.write_text(new_content)


def inject_users_model(models_file: Path, db_choice: str):
    if db_choice == "MongoDB":
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
