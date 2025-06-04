from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import sessionmaker
from .settings import settings
# Fetch the database URL from environment variables



SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in environment variables.")

print("SQLALCHEMY_DATABASE_URL:", SQLALCHEMY_DATABASE_URL)

# Create the async engine
async_engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True,  # Set to False in production to disable logging
    future=True,
    pool_size=5,  # Default number of permanent connections
    max_overflow=10,  # Additional connections allowed
    pool_pre_ping=True,  # Check connection validity before using
    pool_recycle=1800,  # Recycle connections after 30 minutes
    pool_timeout=30  # Wait up to 30 seconds for a connection
)

# Async session maker
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
    class_=AsyncSession
)

# Base class for declarative models
#Base = declarative_base()

# Dependency to get an async database session
async def get_db():
    async with AsyncSessionLocal() as async_db:
        try:
            yield async_db
        finally:
            await async_db.close()


class Base(DeclarativeBase):
    pass

