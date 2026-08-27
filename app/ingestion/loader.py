from pathlib import Path

from pypdf import PdfReader
from docx import Document


SUPPORTED_EXTENSIONS = {
    ".txt",
    ".pdf",
    ".docx",
}


def load_txt(path: Path) -> str:
    return path.read_text(
        encoding="utf-8",
        errors="ignore",
    )


def load_pdf(path: Path) -> str:

    reader = PdfReader(str(path))

    pages = []

    for page in reader.pages:

        text = page.extract_text() or ""

        if text.strip():
            pages.append(text)

    return "\n\n".join(pages)


def load_docx(path: Path) -> str:

    document = Document(str(path))

    paragraphs = [
        paragraph.text
        for paragraph in document.paragraphs
        if paragraph.text.strip()
    ]

    return "\n".join(paragraphs)


def load_document(path: Path) -> str:

    extension = path.suffix.lower()

    if extension == ".txt":
        return load_txt(path)

    if extension == ".pdf":
        return load_pdf(path)

    if extension == ".docx":
        return load_docx(path)

    raise ValueError(
        f"Unsupported document type: {extension}"
    )