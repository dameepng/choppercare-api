from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import init_db
from app.routers import chat, alert
from app.middleware.rate_limit import limiter
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    await init_db()
    yield
    # shutdown (cleanup kalau perlu)


app = FastAPI(
    title="ChopperCare API",
    description="Disaster response chatbot API — IDCamp 2025",
    version="1.0.0",
    lifespan=lifespan,
    # disable docs di production kalau perlu
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url=None,
)

# Rate limiter error handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS — allow choppercare frontend only
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Routers
app.include_router(chat.router, prefix="/api")
app.include_router(alert.router, prefix="/api")


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "choppercare-api"}