# LegalEase

### 🔗 Live app: <a href="https://legal-ease-vert.vercel.app/" target="_blank" rel="noopener noreferrer">legal-ease-vert.vercel.app</a>

An international hackathon-winning, AI-powered platform that demystifies complex legal
documents for the average Indian person. Upload a rental agreement, employment contract,
or notice and get a plain-language breakdown of what it says, what to watch out for, and
grounded answers to your follow-up questions — via web or WhatsApp.

Under the hood, the platform runs on an agentic RAG (Retrieval-Augmented Generation) pipeline purpose-built for Indian law. Uploaded documents and a self-sourced corpus of Indian bare acts and regulations are chunked, embedded, and indexed into a self-hosted vector database, retrieved through a hybrid search layer (dense semantic search combined with BM25 keyword matching, fused via Reciprocal Rank Fusion) — this ensures both conceptual matches ("a clause about wrongful termination") and exact statutory citations ("Section 73") are retrieved reliably. A multi-agent system built with CrewAI handles the analysis end-to-end: dedicated agents parse the document, extract and classify clauses, retrieve relevant legal context, flag risk, and generate the final summary — with a separate Scope Guardrail agent reviewing every output to ensure responses stay within the system's informational scope and clearly defer to a qualified legal professional where appropriate. Follow-up questions are answered by the same retrieval pipeline, grounded jointly in the uploaded document and the underlying legal corpus, and delivered through both the web app and a Twilio-powered WhatsApp integration sharing the identical backend pipeline.

**Disclaimer:** LegalEase is informational only and is not a substitute for professional
legal advice.

## Technology Stack

- **Frontend**: Next.js (App Router, TypeScript, Tailwind CSS) — deployed on Vercel
- **Backend**: FastAPI (Python) — deployed on Render
- **Agents**: CrewAI — a six-agent Analysis Crew (document parsing, clause extraction, legal retrieval, risk analysis, summarization, scope guardrail) and a two-agent Chat Crew (Q&A + guardrail)
- **Retrieval**: Chroma (self-hosted), hybrid dense + BM25 search fused via Reciprocal Rank Fusion, over a self-sourced corpus of Indian bare acts
- **Embeddings**: `BAAI/bge-small-en-v1.5` via `fastembed` (ONNX runtime, local, no GPU or API cost)
- **LLM**: Google Gemini
- **WhatsApp**: Twilio Sandbox
- **Deployment**: Docker on Render (backend) + Vercel (frontend)

## Project Structure

```
LegalEase/
├── frontend/              # Next.js app
│   ├── app/               # Routes: landing, /analyze/[docId], /about, /whatsapp-demo
│   ├── components/        # UploadBox, ChatPanel, ClauseHighlightList, etc.
│   └── lib/                # API client, shared types
├── backend/
│   ├── agents/             # CrewAI agents + Analysis/Chat Crew orchestration
│   ├── api/                # FastAPI routes: documents, chat, WhatsApp webhook
│   ├── retrieval/           # Chroma client, BM25 index, hybrid retriever, embeddings
│   ├── services/            # In-memory job/session/analysis storage
│   ├── tools/               # PDF/Word/Chroma tools used by agents
│   └── tests/
├── corpus/
│   ├── scripts/              # Scraper + Chroma index builder
│   └── chroma_data/           # Baked, committed vector index
└── deployment/
    ├── Dockerfile.backend
    └── render.yaml
```

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.12 (a newer default install may lack prebuilt wheels for some dependencies)
- A [Gemini API key](https://ai.google.dev/) (free tier)
- (Optional, for WhatsApp) A [Twilio](https://www.twilio.com/) account with the WhatsApp Sandbox enabled

### Backend setup

```bash
py -3.12 -m venv .venv
.venv\Scripts\activate          # Windows; source .venv/bin/activate on macOS/Linux
pip install -r backend/requirements.txt
cp .env.example .env            # then add your GEMINI_API_KEY
python -m uvicorn backend.main:app --reload --port 8000
```

The legal corpus (`corpus/chroma_data/`) is already built and committed, so no setup is
needed to query it. To rebuild it from scratch (e.g. after adding more source acts):

```bash
python corpus/scripts/scrape_bare_acts.py
python corpus/scripts/build_corpus_index.py
```

### Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:3000`.

## Deployment

- **Backend**: Render, deployed from [`deployment/Dockerfile.backend`](deployment/Dockerfile.backend) — bakes the legal corpus and embedding model into the image at build time, since Render's free tier has no persistent disk. Set `GEMINI_API_KEY` and `CORS_ORIGINS` (your Vercel URL) as environment variables in the Render dashboard.
- **Frontend**: Vercel, with the project root set to `frontend/` and `NEXT_PUBLIC_API_BASE_URL` pointing at the Render backend's URL.

Both are configured to auto-deploy on every push to `main`.

## Usage

1. Visit the [live app](https://legal-ease-vert.vercel.app/)
2. Upload a PDF or Word document
3. Wait for the plain-language summary and risk-flagged clauses (usually 1–3 minutes)
4. Ask a follow-up question — a relevant example is suggested based on your document's own flagged clauses
5. Or try the same flow on WhatsApp via the Sandbox number shown on the app's WhatsApp page

## Security & Privacy

- Uploaded documents are processed in memory and are not persisted beyond the session
- No user accounts, authentication, or payment infrastructure
- Every analysis and chat response carries a disclaimer and flags anything needing a licensed professional's review

## Non-Goals

- Not a substitute for a licensed lawyer
- Does not cover the entirety of Indian law — corpus coverage is intentionally scoped and documented, not silently incomplete
- Does not monitor for real-time changes in law

## License

This project is for educational and demonstration purposes.
