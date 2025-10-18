from fastapi import FastAPI

from app.core.config import settings
from app.routers.main import api_router

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(api_router)


@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}!"}
