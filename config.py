from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

"""DATABASE_URL = (
    "postgresql+asyncpg://neondb_owner:npg_icM2vRHn6qes@"
    "ep-noisy-king-ah8z3emv-pooler.c-3.us-east-1.aws.neon.tech/neondb"
)"""

DATABASE_URL = "sqlite+aiosqlite:///database.db"


engine = create_async_engine(
    DATABASE_URL,
    echo=False
)

async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_session():
    async with async_session() as session:
        yield session


