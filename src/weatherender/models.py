from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from weatherender.config import Config

_engine: Engine | None = None
_session_factory: sessionmaker[Session] | None = None


def get_engine() -> Engine:
    """Return the module-level SQLAlchemy engine, creating it on first use.

    Deferred so that merely importing this module (e.g. `weatherender
    --help`, static tooling, or an import smoke test) doesn't require a
    valid DATABASE_URL to already be configured.
    """
    global _engine
    if _engine is None:
        _engine = create_engine(Config.DATABASE_URL, pool_size=10, max_overflow=20)
    return _engine


def SessionLocal() -> Session:
    """Return a new SQLAlchemy session, building the session factory lazily."""
    global _session_factory
    if _session_factory is None:
        _session_factory = sessionmaker(bind=get_engine())
    return _session_factory()


class Base(DeclarativeBase):
    pass


class WeatherRequest(Base):
    __tablename__ = "weather_requests"

    id = Column(Integer, primary_key=True)
    city = Column(String(100), nullable=False)
    source = Column(String(10), nullable=False)
    temp_c = Column(Float, nullable=True)
    condition = Column(String(100), nullable=True)
    success = Column(Integer, nullable=False, default=1)
    error_message = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
