from groq import AsyncGroq
from typing import AsyncGenerator

from app.config import settings

client = AsyncGroq(api_key=settings.GROQ_API_KEY)

SYSTEM_PROMPT = """Kamu adalah ChopperCare, asisten tanggap bencana berbasis AI untuk Indonesia.
Kamu membantu masyarakat dengan informasi terkait:
- Prosedur evakuasi dan jalur penyelamatan
- Pertolongan pertama saat bencana
- Kontak darurat BNPB, BPBD, dan layanan darurat
- Informasi terkini situasi bencana berdasarkan dokumen resmi BNPB

Gunakan bahasa Indonesia yang jelas dan mudah dipahami.
Prioritaskan keselamatan jiwa di atas segalanya.
Jika tidak tahu jawabannya, arahkan ke hotline BNPB: 117."""


async def stream_chat(
    messages: list[dict],
    context: str = "",
) -> AsyncGenerator[str, None]:
    """Stream response dari Groq dengan RAG context."""

    system = SYSTEM_PROMPT
    if context:
        system += f"\n\nKonteks dari dokumen BNPB:\n{context}"

    stream = await client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[
            {"role": "system", "content": system},
            *messages,
        ],
        stream=True,
        max_tokens=1024,
        temperature=0.3,  # rendah — disaster info harus akurat
    )

    async for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta