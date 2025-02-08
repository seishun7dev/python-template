import os

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import AsyncAdaptedQueuePool



DATABASE_URL = os.getenv("DATABASE_URL", "mysql+asyncmy://user:password@localhost/mydatabase")

engine = create_async_engine(
    DATABASE_URL,
    poolclass=AsyncAdaptedQueuePool,
    pool_size=5,
    pool_pre_ping=True,
    max_overflow=10,
    pool_recycle=3600
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)