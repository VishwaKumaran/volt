from app.core.config import settings
from motor.motor_asyncio import AsyncIOMotorClient

client: AsyncIOMotorClient | None = None
db = None


async def init_db():
    global client, db
    client = AsyncIOMotorClient(settings.DATABASE_URI)
    db = client[settings.DB_NAME]


async def close_db():
    global client
    if client:
        client.close()
