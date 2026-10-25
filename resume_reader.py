"""
Extracts text from a resume PDF so the candidate can point to a file
instead of pasting text by hand. Uses pypdf (pure Python, no external
binary needed, works offline — no network call, unlike everything
else that touches an external service in this project).
"""

from pathlib import Path
from pypdf import PdfReader


def extract_text_from_pdf(path: str) -> str:
    file_path = Path(path).expanduser()
    if not file_path.exists():
        raise FileNotFoundError(f"No file found at: {file_path}")
    if file_path.suffix.lower() != ".pdf":
        raise ValueError(f"Expected a .pdf file, got: {file_path.suffix}")

    reader = PdfReader(str(file_path))
    text = "\n".join(page.extract_text() or "" for page in reader.pages)

    if not text.strip():
        raise ValueError(
            "No extractable text found in this PDF — it may be a scanned "
            "image rather than real text. Try pasting the resume text instead."
        )

    return text.strip()