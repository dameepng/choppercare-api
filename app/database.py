from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy import text

from app.config import settings

# Convert ke async URL (asyncpg driver)
DATABASE_URL = settings.DATABASE_URL.replace(
    "postgresql://", "postgresql+asyncpg://"
)

engine = create_async_engine(DATABASE_URL, echo=settings.DEBUG)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    """Init pgvector extension + create tables on startup."""
    async with engine.begin() as conn:
        # Enable pgvector
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))

        # Table: document chunks (BNPB knowledge base)
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS bnpb_chunks (
                id          SERIAL PRIMARY KEY,
                content     TEXT NOT NULL,
                source      TEXT,
                page        INT,
                embedding   vector(768),
                created_at  TIMESTAMP DEFAULT NOW()
            )
        """))

        # Index untuk cosine similarity search
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS bnpb_chunks_embedding_idx
            ON bnpb_chunks USING ivfflat (embedding vector_cosine_ops)
            WITH (lists = 100)
        """))

        # Table: chat history
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS chat_sessions (
                id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                session_id  TEXT NOT NULL,
                role        TEXT NOT NULL,
                content     TEXT NOT NULL,
                created_at  TIMESTAMP DEFAULT NOW()
            )
        """))

        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS chat_sessions_session_idx
            ON chat_sessions (session_id, created_at DESC)
        """))

    print("✓ Database initialized")