import taskiq_redis
from taskiq import InMemoryBroker
from app.core.config import settings

if settings.ENVIRONMENT == "local" and not settings.REDIS_URL:
    broker = InMemoryBroker()
else:
    broker = taskiq_redis.ListQueueBroker(settings.REDIS_URL)


@broker.task
async def example_task(name: str) -> str:
    print(f"Executing task for {name}")
    return f"Hello, {name}!"
