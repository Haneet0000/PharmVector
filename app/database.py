from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from app.config import get_settings

settings = get_settings()

engine = create_async_engine(settings.DATABASE_URL, echo=False, future=True)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
