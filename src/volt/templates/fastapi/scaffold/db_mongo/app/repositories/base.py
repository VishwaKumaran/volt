from typing import Generic, TypeVar, Sequence

T = TypeVar("T")


class BaseRepository(Generic[T]):
    model: type[T]

    async def get(self, id: int) -> T | None:
        return await self.model.get(id)

    async def get_multi(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[T]:
        return await self.model.find().skip(skip).limit(limit)

    async def create(self, obj: T) -> T:
        return await self.model.insert_one(obj.model_dump())

    async def delete(self, id: int) -> T | None:
        obj = await self.get(id)
        if not obj:
            return None
        await obj.delete()
        return obj
