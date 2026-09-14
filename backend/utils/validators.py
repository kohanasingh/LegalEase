"""Server-side upload validation (client-side checks in UploadBox are UX only)."""
from backend.utils.document_extraction import SUPPORTED_CONTENT_TYPES

ALLOWED_CONTENT_TYPES = SUPPORTED_CONTENT_TYPES
MAX_UPLOAD_BYTES = 20 * 1024 * 1024  # 20MB


class UploadValidationError(ValueError):
    pass


def validate_upload(filename: str, content_type: str, size_bytes: int) -> None:
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise UploadValidationError(
            f"Unsupported file type: {content_type}. Only PDF and Word (.docx) documents are supported."
        )
    if size_bytes <= 0:
        raise UploadValidationError("Uploaded file is empty.")
    if size_bytes > MAX_UPLOAD_BYTES:
        raise UploadValidationError(f"File exceeds the {MAX_UPLOAD_BYTES // (1024*1024)}MB limit.")
