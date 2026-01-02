from typing import List

from app.models.__MODEL_NAME_LOWER__ import __MODEL_NAME__
from app.repositories.__MODEL_NAME_LOWER__ import __MODEL_NAME__Repository
from app.schemas.__MODEL_NAME_LOWER__ import __MODEL_NAME__Create, __MODEL_NAME__Update
from app.services.base import BaseService


class __MODEL_NAME__Service(BaseService[__MODEL_NAME__]):
    model = __MODEL_NAME__

    def __init__(self, repo: __MODEL_NAME__Repository | None = None):
        self.repo = repo or __MODEL_NAME__Repository()

    async def create(self, obj_in: __MODEL_NAME__Create) -> __MODEL_NAME__:
        return await self.repo.create(obj_in)

    async def get(self, id: int) -> __MODEL_NAME__ | None:
        return await self.repo.get(id)

    async def get_multi(self, skip: int = 0, limit: int = 100) -> List[__MODEL_NAME__]:
        return await self.repo.get_multi(skip, limit)

    async def update(
        self, id: int, obj_in: __MODEL_NAME__Update
    ) -> __MODEL_NAME__ | None:
        db_obj = await self.repo.get(id)
        if not db_obj:
            return None

        return await self.repo.update(db_obj, obj_in)

    async def delete(self, id: int) -> __MODEL_NAME__ | None:
        return await self.repo.delete(id)
