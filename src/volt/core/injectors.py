import re
from pathlib import Path


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
