from app.ingestion.chunker import chunk_text


text = """
Retrieval-Augmented Generation (RAG) combines
information retrieval with generative language models.

The system first loads documents and extracts
their text.

Large documents are then divided into smaller
chunks.

Each chunk is converted into an embedding.

The embeddings are stored in a vector database.

When the user asks a question, the question is
also converted into an embedding.

The vector database searches for similar chunks.

The retrieved chunks are then added to the
prompt sent to the language model.

The language model generates the final answer
using the retrieved context.
"""


chunks = chunk_text(
    text,
    chunk_size=120,
    overlap=30,
)


print(
    f"Created {len(chunks)} chunks"
)


for chunk in chunks:

    print("=" * 60)

    print(
        f"Chunk {chunk.chunk_index}"
    )

    print(
        f"Characters: {len(chunk.text)}"
    )

    print()

    print(chunk.text)