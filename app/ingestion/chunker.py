from dataclasses import dataclass


@dataclass
class TextChunk:
    """
    Represents one piece of a document.

    text:
        The actual text that will be embedded.

    chunk_index:
        Position of this chunk inside the document.
    """

    text: str
    chunk_index: int


def chunk_text(
    text: str,
    chunk_size: int = 1200,
    overlap: int = 200,
) -> list[TextChunk]:

    # -----------------------------------------
    # Validate settings
    # -----------------------------------------

    if chunk_size <= 0:
        raise ValueError(
            "chunk_size must be greater than 0"
        )

    if overlap < 0:
        raise ValueError(
            "overlap cannot be negative"
        )

    if overlap >= chunk_size:
        raise ValueError(
            "overlap must be smaller than chunk_size"
        )

    # -----------------------------------------
    # Clean the text WITHOUT destroying
    # paragraph boundaries.
    # -----------------------------------------

    paragraphs = [
        paragraph.strip()
        for paragraph in text.split("\n")
        if paragraph.strip()
    ]

    if not paragraphs:
        return []

    # -----------------------------------------
    # Combine paragraphs until the chunk
    # reaches approximately chunk_size.
    # -----------------------------------------

    chunks = []

    current_text = ""

    for paragraph in paragraphs:

        # If adding this paragraph keeps us
        # within our target size, add it.
        if (
            len(current_text)
            + len(paragraph)
            + 1
            <= chunk_size
        ):

            if current_text:
                current_text += "\n\n"

            current_text += paragraph

        else:

            # Store the current chunk.
            if current_text:
                chunks.append(current_text)

            # Start a new chunk.
            current_text = paragraph

    # Don't forget the final chunk.
    if current_text:
        chunks.append(current_text)

    # -----------------------------------------
    # Add overlap between neighboring chunks.
    #
    # This helps prevent important information
    # from being lost at chunk boundaries.
    # -----------------------------------------

    final_chunks = []

    for index, chunk in enumerate(chunks):

        if index == 0:

            final_chunks.append(
                TextChunk(
                    text=chunk,
                    chunk_index=index,
                )
            )

            continue

        previous_chunk = chunks[index - 1]

        # Take the last `overlap` characters
        # from the previous chunk.
        overlap_text = previous_chunk[
            -overlap:
        ]

        combined = (
            overlap_text
            + "\n\n"
            + chunk
        )

        final_chunks.append(
            TextChunk(
                text=combined,
                chunk_index=index,
            )
        )

    return final_chunks