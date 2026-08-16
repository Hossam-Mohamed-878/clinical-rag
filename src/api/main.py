from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.core.config import settings
from api.routes.chat import router as chat_router


def create_app() -> FastAPI:
    """Application factory — builds and configures the FastAPI instance."""

    app = FastAPI(
        title="AI Agent Chat API",
        description="Streaming chat interface for the Ollama-powered agent.",
        version="1.0.0",
        debug=settings.debug,
    )

    # ── Middleware ────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Routers ───────────────────────────────────────────────────────────────
    app.include_router(chat_router)

    # ── Utility endpoints ─────────────────────────────────────────────────────
    @app.get("/health", tags=["meta"])
    def health() -> dict:
        return {"status": "ok", "model": settings.working_model}

    return app


app = create_app()
