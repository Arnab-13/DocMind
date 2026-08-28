from pathlib import Path
from uuid import uuid4

from qdrant_client.models import PointStruct

from app.ingestion.loader import load_document
from app.ingestion.chunker import chunk_text
from app.ingestion.embedder import embed_texts
from app.database.qdrant_db import upsert_points


async def ingest_file(
    path: Path,
) -> dict:

    # -----------------------------------------
    # STEP 1
    # Extract text from the document.
    # -----------------------------------------

    text = load_document(path)

    if not text.strip():
        raise ValueError(
            "Document contains no readable text."
        )

    # -----------------------------------------
    # STEP 2
    # Split the document into chunks.
    # -----------------------------------------

    chunks = chunk_text(text)

    if not chunks:
        raise ValueError(
            "Document produced no chunks."
        )

    # -----------------------------------------
    # STEP 3
    # Extract just the text from each chunk.
    #
    # Example:
    #
    # [
    #   "RAG is...",
    #   "Embeddings are...",
    #   "Qdrant stores..."
    # ]
    # -----------------------------------------

    texts = [
        chunk.text
        for chunk in chunks
    ]

    # -----------------------------------------
    # STEP 4
    # Send all chunks to the FREE
    # OpenRouter embedding model.
    #
    # Each chunk becomes a 1024-dimensional
    # vector.
    # -----------------------------------------

    vectors = await embed_texts(texts)

    # -----------------------------------------
    # STEP 5
    # Create Qdrant points.
    #
    # A point contains:
    #
    # ID
    # Vector
    # Metadata/payload
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
                "text": chunk.text,
                "source": path.name,
                "chunk_index": chunk.chunk_index,
            },
        )

        points.append(point)

    # -----------------------------------------
    # STEP 6
    # Send the vectors to Qdrant Cloud.
    # -----------------------------------------

    upsert_points(points)

    return {
        "source": path.name,
        "characters": len(text),
        "chunks": len(chunks),
        "vectors_stored": len(points),
    }