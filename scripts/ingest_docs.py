"""
Script ingest dokumen BNPB ke PostgreSQL pgvector.
Jalankan sekali: python scripts/ingest_docs.py

Taruh PDF BNPB di folder docs/
"""
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from sentence_transformers import SentenceTransformer

from app.config import settings

DATABASE_URL = settings.DATABASE_URL.replace(
    "postgresql://", "postgresql+asyncpg://"
)
engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

model = SentenceTransformer(settings.EMBED_MODEL, trust_remote_code=True)

splitter = RecursiveCharacterTextSplitter(
    chunk_size=settings.CHUNK_SIZE,
    chunk_overlap=settings.CHUNK_OVERLAP,
    separators=["\n\n", "\n", ". ", " "],
)


def read_pdf(filepath: str) -> list[dict]:
    reader = PdfReader(filepath)
    pages = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text and text.strip():
            pages.append({"content": text, "page": i + 1})
    return pages


async def ingest_file(filepath: str, db: AsyncSession):
    filename = os.path.basename(filepath)
    print(f"  Processing: {filename}")

    pages = read_pdf(filepath)
    total_chunks = 0

    for page_data in pages:
        chunks = splitter.split_text(page_data["content"])
        for chunk in chunks:
            if len(chunk.strip()) < 50:
                continue  # skip chunk terlalu pendek

            # nomic-embed-text pakai prefix untuk dokumen
            embedding = model.encode(
                f"search_document: {chunk}",
                normalize_embeddings=True,
            ).tolist()

            await db.execute(
                text("""
                    INSERT INTO bnpb_chunks (content, source, page, embedding)
                    VALUES (:content, :source, :page, CAST(:embedding AS vector))
                """),
                {
                    "content": chunk,
                    "source": filename,
                    "page": page_data["page"],
                    "embedding": str(embedding),
                },
            )
            total_chunks += 1

    await db.commit()
    print(f"  ✓ {filename}: {total_chunks} chunks ingested")


async def main():
    docs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs")
    pdf_files = [
        os.path.join(docs_dir, f)
        for f in os.listdir(docs_dir)
        if f.endswith(".pdf")
    ]

    if not pdf_files:
        print("❌ Tidak ada PDF di folder docs/")
        return

    print(f"Found {len(pdf_files)} PDF files, starting ingest...")

    async with AsyncSessionLocal() as db:
        for filepath in pdf_files:
            await ingest_file(filepath, db)

    print("\n✓ Ingest selesai!")


if __name__ == "__main__":
    asyncio.run(main())
