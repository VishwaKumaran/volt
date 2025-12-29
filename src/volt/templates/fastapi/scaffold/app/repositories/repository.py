from typing import List, Optional
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.__MODEL_NAME_LOWER__ import __MODEL_NAME__
from app.schemas.__MODEL_NAME_LOWER__ import __MODEL_NAME__Create, __MODEL_NAME__Update


class __MODEL_NAME__Repository:
    async def create(
        self, session: AsyncSession, obj_in: __MODEL_NAME__Create
    ) -> __MODEL_NAME__:
        db_obj = __MODEL_NAME__.model_validate(obj_in)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def get(self, session: AsyncSession, id: int) -> Optional[__MODEL_NAME__]:
        return await session.get(__MODEL_NAME__, id)

    async def get_multi(
        self,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> List[__MODEL_NAME__]:
        statement = select(__MODEL_NAME__).offset(skip).limit(limit)
        result = await session.exec(statement)
        return result.all()

    async def update(
        self,
        session: AsyncSession,
        db_obj: __MODEL_NAME__,
        obj_in: __MODEL_NAME__Update,
    ) -> __MODEL_NAME__:
        obj_data = obj_in.model_dump(exclude_unset=True)
        for key, value in obj_data.items():
            setattr(db_obj, key, value)

        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def delete(self, session: AsyncSession, id: int) -> Optional[__MODEL_NAME__]:
        db_obj = await session.get(__MODEL_NAME__, id)
        if not db_obj:
            return None

        await session.delete(db_obj)
        await session.commit()
        return db_obj
