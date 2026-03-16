from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text


async def save_message(
    session_id: str,
    role: str,
    content: str,
    db: AsyncSession,
) -> None:
    await db.execute(
        text("""
            INSERT INTO chat_sessions (session_id, role, content)
            VALUES (:session_id, :role, :content)
        """),
        {"session_id": session_id, "role": role, "content": content},
    )
    await db.commit()


async def get_history(
    session_id: str,
    db: AsyncSession,
    limit: int = 10,
) -> list[dict]:
    """Ambil N pesan terakhir untuk context window."""
    result = await db.execute(
        text("""
            SELECT role, content FROM chat_sessions
            WHERE session_id = :session_id
            ORDER BY created_at DESC
            LIMIT :limit
        """),
        {"session_id": session_id, "limit": limit},
    )
    rows = result.fetchall()
    # Reverse supaya urutan kronologis
    return [{"role": r.role, "content": r.content} for r in reversed(rows)]