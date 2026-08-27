from dataclasses import dataclass


@dataclass
class TextChunk:
    text: str
    chunk_index: int


def chunk_text(
    text: str,
    chunk_size: int = 1200,
    overlap: int = 200,
) -> list[TextChunk]:

    text = " ".join(text.split())

    if not text:
        return []

    if overlap >= chunk_size:
        raise ValueError(
            "overlap must be smaller than chunk_size"
        )

    chunks = []

    start = 0
    chunk_index = 0

    while start < len(text):

        end = min(
            start + chunk_size,
            len(text),
        )

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(
                TextChunk(
                    text=chunk,
                    chunk_index=chunk_index,
                )
            )

            chunk_index += 1

        if end >= len(text):
            break

        start = end - overlap

    return chunks