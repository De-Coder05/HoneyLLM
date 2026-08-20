"""FastAPI entrypoint — Honey-LLM gateway.

Phase 0/1: health + Ollama-health checks, CORS for the Next.js dev server, and
the placeholder /api/chat + /api/dashboard routers mounted. Every request will
eventually pass through the Intent Sieve here (Architecture.md §1); the routers
are already positioned for that.
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.models.schemas import HealthResponse, OllamaHealth
from app.routers import admin, chat, dashboard
from app.services.ollama_client import OllamaClient, OllamaError

VERSION = "0.1.0"  # Phase 0/1 skeleton

settings = get_settings()
configure_logging(settings.log_level)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting %s (env=%s)", settings.app_name, settings.environment)
    client = OllamaClient()
    if await client.is_reachable():
        models = await client.list_models()
        logger.info("Ollama reachable — %d models available", len(models))
    else:
        # Not fatal for the skeleton, but loud: the sieve depends on this.
        logger.warning("Ollama NOT reachable at %s", settings.ollama_base_url)
    yield
    logger.info("Shutting down %s", settings.app_name)


app = FastAPI(title=settings.app_name, version=VERSION, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(dashboard.router)
app.include_router(admin.router)


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health() -> HealthResponse:
    return HealthResponse(
        app=settings.app_name,
        environment=settings.environment,
        version=VERSION,
    )


@app.get("/health/ollama", response_model=OllamaHealth, tags=["health"])
async def ollama_health() -> OllamaHealth:
    """Reports whether the local inference backend + required models are present.

    This is the Phase 1 'validate against real hardware, not assumed' check in
    live form — the sieve cannot function unless this is green.
    """
    client = OllamaClient()
    try:
        models = await client.list_models()
    except OllamaError as exc:
        return OllamaHealth(
            reachable=False,
            base_url=settings.ollama_base_url,
            detail=str(exc),
        )
    return OllamaHealth(
        reachable=True,
        base_url=settings.ollama_base_url,
        models_available=models,
        sieve_model_present=settings.sieve_model in models,
        rag_model_present=settings.rag_model in models,
    )
