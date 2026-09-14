from dataclasses import dataclass
import re


@dataclass
class TextChunk:
    """
    Represents one chunk of a document.
    """

    text: str
    chunk_index: int


def chunk_text(
    text: str,
    chunk_size: int = 900,
    overlap: int = 150,
) -> list[TextChunk]:
    """
    Split a document into sentence-aware chunks.

    The chunker tries to keep sentences together instead
    of cutting through words randomly.

    chunk_size:
        Approximate maximum number of characters per chunk.

    overlap:
        Number of characters from the previous chunk
        that should be reused for context.
    """

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
    # Clean the document
    # -----------------------------------------

    text = text.strip()

    if not text:
        return []

    # Replace multiple spaces/newlines with one space.
    text = re.sub(r"\s+", " ", text)

    # -----------------------------------------
    # Split into sentences
    # -----------------------------------------

    sentences = re.split(
        r"(?<=[.!?])\s+",
        text,
    )

    sentences = [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]

    # -----------------------------------------
    # Build chunks
    # -----------------------------------------

    chunks = []

    current_sentences = []
    current_length = 0
    chunk_index = 0

    for sentence in sentences:

        sentence_length = len(sentence)

        # -------------------------------------
        # If adding this sentence would make
        # the chunk too large, save the current
        # chunk first.
        # -------------------------------------

        if (
            current_sentences
            and current_length + 1 + sentence_length
            > chunk_size
        ):

            chunk_text_value = " ".join(
                current_sentences
            ).strip()

            chunks.append(
                TextChunk(
                    text=chunk_text_value,
                    chunk_index=chunk_index,
                )
            )

            chunk_index += 1

            # ---------------------------------
            # Create overlap.
            #
            # We keep the last sentence(s)
            # from the previous chunk until
            # we approach the overlap size.
            # ---------------------------------

            overlap_sentences = []
            overlap_length = 0

            for previous_sentence in reversed(
                current_sentences
            ):

                if (
                    overlap_length
                    + len(previous_sentence)
                    > overlap
                ):
                    break

                overlap_sentences.insert(
                    0,
                    previous_sentence,
                )

                overlap_length += (
                    len(previous_sentence)
                )

            current_sentences = overlap_sentences

            current_length = sum(
                len(sentence)
                for sentence in current_sentences
            )

        current_sentences.append(sentence)

        current_length = sum(
            len(sentence)
            for sentence in current_sentences
        )

    # -----------------------------------------
    # Save final chunk
    # -----------------------------------------

    if current_sentences:

        chunk_text_value = " ".join(
            current_sentences
        ).strip()

        chunks.append(
            TextChunk(
                text=chunk_text_value,
                chunk_index=chunk_index,
            )
        )

    return chunks