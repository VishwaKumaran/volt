from typing import List

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.__MODEL_NAME_LOWER__ import __MODEL_NAME__
from app.schemas.__MODEL_NAME_LOWER__ import __MODEL_NAME__Create, __MODEL_NAME__Update
from app.repositories.__MODEL_NAME_LOWER__ import __MODEL_NAME__Repository


class __MODEL_NAME__Service:
    def __init__(self, repo: __MODEL_NAME__Repository | None = None):
        self.repo = repo or __MODEL_NAME__Repository()

    async def create___MODEL_NAME_LOWER__(
        self,
        session: AsyncSession,
        obj_in: __MODEL_NAME__Create,
    ) -> __MODEL_NAME__:
        return await self.repo.create(session, obj_in)

    async def get___MODEL_NAME_LOWER__(
        self,
        session: AsyncSession,
        id: int,
    ) -> __MODEL_NAME__ | None:
        return await self.repo.get(session, id)

    async def get_multi___MODEL_NAME_LOWER__(
        self,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> List[__MODEL_NAME__]:
        return await self.repo.get_multi(session, skip, limit)

    async def update___MODEL_NAME_LOWER__(
        self,
        session: AsyncSession,
        id: int,
        obj_in: __MODEL_NAME__Update,
    ) -> __MODEL_NAME__ | None:
        db_obj = await self.repo.get(session, id)
        if not db_obj:
            return None

        return await self.repo.update(session, db_obj, obj_in)

    async def delete___MODEL_NAME_LOWER__(
        self,
        session: AsyncSession,
        id: int,
    ) -> __MODEL_NAME__ | None:
        return await self.repo.delete(session, id)
