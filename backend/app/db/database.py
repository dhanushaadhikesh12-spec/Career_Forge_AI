from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings
import logging

from sqlalchemy.pool import NullPool

logger = logging.getLogger(__name__)

engine_kwargs = {"echo": settings.DB_ECHO}  # Set DB_ECHO=true in .env to enable SQL query logging
if "sqlite" in settings.DATABASE_URL:
    engine_kwargs["connect_args"] = {"check_same_thread": False}
elif settings.APP_ENV == "test":
    engine_kwargs["poolclass"] = NullPool
else:
    engine_kwargs["pool_size"] = 10
    engine_kwargs["max_overflow"] = 20
    engine_kwargs["pool_pre_ping"] = True

engine = create_async_engine(
    settings.DATABASE_URL,
    **engine_kwargs
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Create all tables. Use Alembic for production migrations."""
    async with engine.begin() as conn:
        from app.models import user, content, test, coding, analytics, chat  # noqa
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables initialized.")
