import asyncio

from app.ingestion.embedder import embed_one
from app.retrieval.retriever import hybrid_retrieve


async def main():
    question = "What is the name of the product?"
    # question = "How are embeddings used in RAG?"

    print(f"\nQuestion: {question}\n")

    # Create the query embedding.
    query_vector = await embed_one(question)

    # Run hybrid retrieval.
    results = hybrid_retrieve(
        question=question,
        query_vector=query_vector,
        top_k=5,
    )

    if not results:
        print("❌ No results found.")
        return

    print(f"Found {len(results)} results:\n")

    for rank, point in enumerate(results, start=1):
        payload = point.payload or {}

        print(f"--- Result {rank} ---")
        print(f"ID: {point.id}")
        print(f"Score: {point.score}")
        print(f"Source: {payload.get('source', 'Unknown')}")
        print(f"Text: {payload.get('text', '')}")
        print()


if __name__ == "__main__":
    asyncio.run(main())