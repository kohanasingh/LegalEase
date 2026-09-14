"""
Single dispatch point from a file's content type to the right text
extractor. Shared by the web upload endpoint and the WhatsApp webhook so
neither channel duplicates this logic (CLAUDE.md non-negotiable #5).
"""
from backend.tools.docx_parser_tool import extract_text_from_docx_bytes
from backend.tools.pdf_parser_tool import extract_text_from_pdf_bytes

DOCX_CONTENT_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

EXTRACTORS = {
    "application/pdf": extract_text_from_pdf_bytes,
    DOCX_CONTENT_TYPE: extract_text_from_docx_bytes,
}

SUPPORTED_CONTENT_TYPES = set(EXTRACTORS)


def extract_text(content_type: str, data: bytes) -> str:
    extractor = EXTRACTORS.get(content_type)
    if extractor is None:
        raise ValueError(f"Unsupported content type: {content_type}")
    return extractor(data)
