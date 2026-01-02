from typing import Generic, TypeVar, Sequence
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

T = TypeVar("T")


class BaseRepository(Generic[T]):
    model: type[T]

    async def get(self, session: AsyncSession, id: int) -> T | None:
        return await session.get(self.model, id)

    async def get_multi(
        self,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[T]:
        result = await session.exec(select(self.model).offset(skip).limit(limit))
        return result.all()

    async def create(self, session: AsyncSession, obj: T) -> T:
        session.add(obj)
        await session.commit()
        await session.refresh(obj)
        return obj

    async def delete(self, session: AsyncSession, id: int) -> T | None:
        obj = await self.get(session, id)
        if not obj:
            return None
        await session.delete(obj)
        await session.commit()
        return obj
