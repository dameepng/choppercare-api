from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from sentence_transformers import SentenceTransformer

from app.config import settings

# Load model sekali saat startup
_model = None


def get_embed_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(
            settings.EMBED_MODEL,
            trust_remote_code=True,  # required untuk nomic-embed-text
        )
    return _model


def embed_text(text_input: str) -> list[float]:
    """Embed single query string."""
    model = get_embed_model()
    # nomic-embed-text pakai prefix untuk query
    embedding = model.encode(
        f"search_query: {text_input}",
        normalize_embeddings=True,
    )
    return embedding.tolist()


async def retrieve_context(query: str, db: AsyncSession) -> str:
    """Cari dokumen BNPB yang relevan via cosine similarity."""
    query_embedding = embed_text(query)

    result = await db.execute(
        text("""
            SELECT content, source, page,
                   1 - (embedding <=> :embedding::vector) AS similarity
            FROM bnpb_chunks
            WHERE 1 - (embedding <=> :embedding::vector) > 0.5
            ORDER BY similarity DESC
            LIMIT :top_k
        """),
        {
            "embedding": str(query_embedding),
            "top_k": settings.TOP_K_RESULTS,
        },
    )

    rows = result.fetchall()
    if not rows:
        return ""

    context_parts = []
    for row in rows:
        source_info = f"[{row.source}, hal. {row.page}]" if row.source else ""
        context_parts.append(f"{source_info}\n{row.content}")

    return "\n\n---\n\n".join(context_parts)