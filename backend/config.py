"""Env-driven settings, shared across the FastAPI app, agents, and retrieval layer."""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BACKEND_DIR = Path(__file__).resolve().parent
REPO_ROOT = BACKEND_DIR.parent

CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", str(REPO_ROOT / "corpus" / "chroma_data"))
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
LEGAL_CORPUS_COLLECTION = "legal_corpus"
USER_DOCUMENTS_COLLECTION = "user_documents"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# gemini-3.6-flash (flagship) free tier is capped at ~20 requests/day - far too
# low for a multi-agent crew. gemini-3.1-flash-lite's free tier is 15 RPM /
# 1000 req/day, which is what this project's "conserve free-tier quota"
# design principle actually needs (see CHANGES.md).
AGENT_LLM_MODEL = "gemini/gemini-3.1-flash-lite"
AGENT_MAX_RPM = 12

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")
