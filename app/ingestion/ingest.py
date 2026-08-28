from pathlib import Path
from uuid import uuid4
import hashlib

from qdrant_client.models import PointStruct

from app.ingestion.loader import load_document
from app.ingestion.chunker import chunk_text
from app.ingestion.embedder import embed_texts

from app.database.qdrant_db import (
    upsert_points,
    delete_document,
)


def calculate_document_id(
    path: Path,
) -> str:
    """
    Create a stable ID for the document.

    We use SHA-256 of the file contents.

    Same file  -> same document_id
    Changed file -> different document_id
    """

    file_bytes = path.read_bytes()

    return hashlib.sha256(
        file_bytes
    ).hexdigest()


async def ingest_file(
    path: Path,
) -> dict:

    # -----------------------------------------
    # STEP 1
    # Create a unique ID based on file contents.
    # -----------------------------------------

    document_id = calculate_document_id(
        path
    )

    # -----------------------------------------
    # Remove an older copy of this document.
    # -----------------------------------------

    delete_document(
        document_id
    )

    # -----------------------------------------
    # STEP 2
    # Extract text from the document.
    # -----------------------------------------

    text = load_document(path)

    if not text.strip():
        raise ValueError(
            "Document contains no readable text."
        )

    # -----------------------------------------
    # STEP 3
    # Split document into chunks.
    # -----------------------------------------

    chunks = chunk_text(text)

    if not chunks:
        raise ValueError(
            "Document produced no chunks."
        )

    # -----------------------------------------
    # STEP 4
    # Extract text from each chunk.
    # -----------------------------------------

    texts = [
        chunk.text
        for chunk in chunks
    ]

    # -----------------------------------------
    # STEP 5
    # Generate embeddings using OpenRouter.
    # -----------------------------------------

    vectors = await embed_texts(
        texts
    )

    # -----------------------------------------
    # STEP 6
    # Create Qdrant points.
    # -----------------------------------------

    points = []

    for chunk, vector in zip(
        chunks,
        vectors,
    ):

        point = PointStruct(

            id=str(uuid4()),

            vector=vector,

            payload={
                # Stable document identity
                "document_id": document_id,

                # Original filename
                "source": path.name,

                # Which chunk this is
                "chunk_index": chunk.chunk_index,

                # Actual text
                "text": chunk.text,
            },
        )

        points.append(point)

    # -----------------------------------------
    # STEP 7
    # Store vectors in Qdrant.
    # -----------------------------------------

    upsert_points(points)

    return {
        "document_id": document_id,
        "source": path.name,
        "characters": len(text),
        "chunks": len(chunks),
        "vectors_stored": len(points),
    }