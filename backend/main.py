"""FastAPI entrypoint. Serves both the web frontend and (from Stage 6) WhatsApp — one backend, one pipeline (CLAUDE.md)."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend import config
from backend.api import chat_routes, document_routes, whatsapp_routes

app = FastAPI(title="LegalEase API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(document_routes.router)
app.include_router(chat_routes.router)
app.include_router(whatsapp_routes.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
