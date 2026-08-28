from app.ingestion.chunker import chunk_text


text = """
Retrieval-Augmented Generation (RAG) combines
information retrieval with text generation.

A RAG system first searches a knowledge base
for relevant information.

The retrieved information is then provided
to a language model as context.

The language model uses this context to
generate a grounded answer.
"""


chunks = chunk_text(
    text,
    chunk_size=120,
    overlap=30,
)


print(
    f"Created {len(chunks)} chunks\n"
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