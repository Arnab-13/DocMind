import asyncio

from app.ingestion.embedder import embed_one
from app.retrieval.retriever import retrieve


async def main():

    # This is the same type of question
    # a real user will eventually ask.
    question = (
        "What is the default maximum chunk size?"
    )

    # Convert question into a vector.
    query_vector = await embed_one(
        question
    )

    print(
        "Question vector dimension:",
        len(query_vector),
    )

    # Search Qdrant.
    results = retrieve(
        query_vector=query_vector,
        top_k=5,
    )

    print("\nRetrieved chunks:")
    print("-" * 50)

    for i, point in enumerate(
        results,
        start=1,
    ):

        payload = point.payload or {}

        print(f"\nResult {i}")

        print(
            "Score:",
            point.score,
        )

        print(
            "Source:",
            payload.get("source"),
        )

        print(
            "Chunk:",
            payload.get("chunk_index"),
        )

        print(
            "Text:",
            payload.get("text"),
        )


if __name__ == "__main__":

    asyncio.run(main())