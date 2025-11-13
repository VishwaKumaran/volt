async def delete_user(User, username):
    if hasattr(User, "find_one"):  # Beanie
        user = await User.find_one(User.username == username)
        if user:
            await user.delete()
    else:  # SQLModel
        from sqlalchemy import delete
        from app.core.db import async_session
        async with async_session() as session:
            await session.execute(delete(User).where(User.username == username))
            await session.commit()


async def find_user(User, username):
    if hasattr(User, "find_one"):
        return await User.find_one(User.username == username)
    else:
        from app.core.db import async_session
        async with async_session() as session:
            return await session.execute(User.select().where(User.username == username))
