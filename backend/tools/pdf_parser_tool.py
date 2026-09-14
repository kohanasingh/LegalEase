"""
PyMuPDF-based PDF text extraction. `extract_text_from_pdf_bytes` is the
core implementation, used directly by the upload pipeline (no temp file
needed) and wrapped below as a CrewAI tool for the Document Parser Agent
(Stage 4), which works from a file path instead.
"""
import pymupdf
from crewai.tools import tool


def extract_text_from_pdf_bytes(data: bytes) -> str:
    with pymupdf.open(stream=data, filetype="pdf") as doc:
        return "\n\n".join(page.get_text() for page in doc)


@tool("PDFParserTool")
def pdf_parser_tool(file_path: str) -> str:
    """Extracts structured plain text from a PDF file at the given path."""
    with open(file_path, "rb") as f:
        return extract_text_from_pdf_bytes(f.read())
