import json
import asyncio
import logging
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.chat import ChatRequest
from app.rag.pipeline import retrieve_context
from app.services.groq_client import stream_chat
from app.services.history import save_message, get_history
from app.middleware.rate_limit import limiter
from app.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/chat")
@limiter.limit(settings.RATE_LIMIT)
async def chat(
    request: Request,
    body: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    """SSE streaming chat endpoint."""

    async def event_stream():
        full_response = ""
        try:
            # 1. Ambil history session
            history = await get_history(body.session_id, db)

            # 2. Tambah pesan user ke history
            history.append({"role": "user", "content": body.message})

            # 3. RAG: retrieve context dari BNPB docs
            context = await retrieve_context(body.message, db)

            # 4. Stream dari Groq
            async for token in stream_chat(history, context):
                full_response += token
                # SSE format: data: <json>\n\n
                yield f"data: {json.dumps({'token': token})}\n\n"
                await asyncio.sleep(0)  # yield ke event loop

            # 5. Kirim signal selesai
            yield f"data: {json.dumps({'done': True})}\n\n"

            # 6. Save ke DB (async, tidak block stream)
            await save_message(body.session_id, "user", body.message, db)
            await save_message(body.session_id, "assistant", full_response, db)

        except Exception as e:
            logger.exception("Chat streaming failed")
            yield f"data: {json.dumps({'error': 'Layanan AI sedang bermasalah. Coba lagi sebentar.', 'detail': str(e)})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # disable Nginx buffering untuk SSE
            "Connection": "keep-alive",
        },
    )
