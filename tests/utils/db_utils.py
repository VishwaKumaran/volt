async def delete_user(User, username):
    if hasattr(User, "find_one"):  # Beanie
        user = await User.find_one(User.username == username)
        if user:
            await user.delete()
    else:  # SQLModel
        from sqlmodel import delete
        from app.core.db import async_session

        async with async_session() as session:
            await session.execute(delete(User).where(User.username == username))
            await session.commit()


async def find_user(User, username):
    if hasattr(User, "find_one"):
        return await User.find_one(User.username == username)
    else:
        from app.core.db import async_session
        from sqlmodel import select

        async with async_session() as session:
            res = await session.execute(select(User).where(User.username == username))
            return res.scalar_one_or_none()
