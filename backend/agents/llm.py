"""Shared LLM instance for all agents — one provider config point."""
from crewai import LLM

from backend import config

_llm: LLM | None = None


def get_llm() -> LLM:
    global _llm
    if _llm is None:
        if not config.GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY is not set — add it to .env before running agents.")
        _llm = LLM(model=config.AGENT_LLM_MODEL, api_key=config.GEMINI_API_KEY, temperature=0.2)
    return _llm
