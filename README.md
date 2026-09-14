# LegalEase

AI-powered legal document analysis for the average Indian person. Upload a
contract, rental agreement, or notice and get a plain-language summary,
risk-flagged clauses, and grounded follow-up Q&A — via web or WhatsApp.

Built as a portfolio project demonstrating a real agentic RAG system
(CrewAI + hybrid retrieval over a self-sourced corpus of Indian law), not a
production legal product. See [PROJECT.md](PROJECT.md) for product intent,
[ARCHITECTURE.md](ARCHITECTURE.md) for the full system design, and
[BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md) for build order and setup.

**Disclaimer:** LegalEase provides informational summaries only and is not a
substitute for professional legal advice.

## Stack

Next.js (Vercel) · FastAPI (Render) · CrewAI · Chroma (self-hosted, hybrid
dense + BM25 retrieval) · `bge-small-en-v1.5` embeddings · Twilio WhatsApp
Sandbox.

## Status

Under active build, following the staged order in BUILD_INSTRUCTIONS.md.
