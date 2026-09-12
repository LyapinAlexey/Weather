from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from weatherender.config import Config

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    """Return the module-level async SQLAlchemy engine, created on first use.

    Deferred for the same reason as the sync engine in `models.py`:
    importing this module shouldn't require DATABASE_URL to already be set.
    """
    global _engine
    if _engine is None:
        if Config.DATABASE_URL is None:
            raise ValueError("DATABASE_URL is not set, cannot build ASYNC_DATABASE_URL")
        async_database_url = Config.DATABASE_URL.replace(
            "postgresql://", "postgresql+asyncpg://", 1
        )
        _engine = create_async_engine(
            async_database_url,
            pool_size=10,
            max_overflow=20,
        )
    return _engine


def AsyncSessionLocal() -> AsyncSession:
    """Return a new async SQLAlchemy session, building the factory lazily."""
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(get_engine(), expire_on_commit=False)
    return _session_factory()
