"""
QA Agent (ARCHITECTURE.md §2): answers follow-up questions grounded in
both the current document and the legal corpus, using the same
ChromaRetrieverTool the Legal Retriever Agent uses (scope parameter
switches between "user_document" and "legal_corpus").
"""
from crewai import Agent

from backend.agents.llm import get_llm
from backend.tools.chroma_retriever_tool import chroma_retriever_tool


def build_agent() -> Agent:
    return Agent(
        role="Document & Law Q&A Agent",
        goal=(
            "Answer the user's question about their uploaded document. Use ChromaRetrieverTool "
            "with scope='user_document' (and the given doc_id) to find relevant parts of their "
            "document, and scope='legal_corpus' to find relevant Indian law. Ground your answer "
            "in what was actually retrieved — clearly note which parts come from 'your document' "
            "versus 'Indian law'. If the retrieved content doesn't support a confident answer, "
            "say so rather than speculating."
        ),
        backstory=(
            "A helpful assistant who answers questions about a specific contract by actually "
            "checking the document and the relevant law, rather than guessing from general "
            "knowledge."
        ),
        tools=[chroma_retriever_tool],
        llm=get_llm(),
        verbose=False,
    )
