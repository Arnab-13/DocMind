import asyncio

from app.ingestion.embedder import embed_one
from app.retrieval.retriever import hybrid_retrieve


# -----------------------------------------
# Test questions
# -----------------------------------------
#
# These questions test both:
#
# 1. Questions that SHOULD retrieve context.
# 2. Questions that SHOULD NOT retrieve context.
#
# The expected source lets us verify that
# the correct document was retrieved.
# -----------------------------------------

TEST_CASES = [
    {
        "question": "How are embeddings used in RAG?",
        "expected_source": "rag_test.txt",
        "should_find_context": True,
    },
    {
        "question": "What is the difference between RAG and fine-tuning?",
        "expected_source": "rag_test.txt",
        "should_find_context": True,
    },
    {
        "question": "What is the population of Japan?",
        "expected_source": None,
        "should_find_context": False,
    },
    {
        "question": "What is the name of the product?",
        "expected_source": "test1.txt",
        "should_find_context": True,
    },
]


async def main():

    print("\n")
    print("=" * 70)
    print("DocMind Hybrid RAG Evaluation")
    print("=" * 70)

    passed = 0
    failed = 0

    for index, test_case in enumerate(
        TEST_CASES,
        start=1,
    ):

        question = test_case["question"]

        expected_source = test_case["expected_source"]

        should_find_context = (
            test_case["should_find_context"]
        )

        print("\n")
        print(f"TEST {index}")
        print("-" * 70)
        print(f"Question: {question}")

        # -----------------------------------------
        # Step 1:
        # Convert the question into an embedding.
        # -----------------------------------------

        query_vector = await embed_one(
            question
        )

        print(
            f"Embedding dimension: {len(query_vector)}"
        )

        # -----------------------------------------
        # Step 2:
        # Hybrid retrieval
        #
        # Combines:
        # - Dense semantic search
        # - BM25 keyword search
        # - RRF ranking
        # -----------------------------------------

        results = hybrid_retrieve(
            question=question,
            query_vector=query_vector,
            top_k=5,
        )

        print(
            f"Retrieved chunks: {len(results)}"
        )

        # -----------------------------------------
        # Step 3:
        # Evaluate retrieval.
        # -----------------------------------------

        if should_find_context:

            if not results:

                print(
                    "❌ FAIL: No context retrieved."
                )

                failed += 1
                continue

            sources = [
                point.payload.get("source")
                for point in results
                if point.payload
            ]

            print(
                f"Sources: {sources}"
            )

            top_source = sources[0] if sources else None

            print(
                f"Top result: {top_source}"
            )

            print(
                f"Expected:   {expected_source}"
            )

            if top_source == expected_source:

                print(
                    "✅ PASS: Expected document ranked #1."
                )

                passed += 1

            else:

                print(
                    "❌ FAIL: Expected document was not ranked #1."
                )

                failed += 1

        else:

            if not results:

                print(
                    "✅ PASS: No irrelevant context retrieved."
                )

                passed += 1

            else:

                print(
                    "⚠️ FAIL: Irrelevant context was retrieved."
                )

                for point in results:

                    payload = point.payload or {}

                    print(
                        f"Source: "
                        f"{payload.get('source', 'Unknown')}"
                    )

                    print(
                        f"Hybrid score: {point.score}"
                    )

                failed += 1

    # -----------------------------------------
    # Final evaluation summary
    # -----------------------------------------

    total = passed + failed

    print("\n")
    print("=" * 70)
    print("Evaluation Summary")
    print("=" * 70)

    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total:  {total}")

    if total > 0:

        accuracy = (
            passed / total
        ) * 100

        print(
            f"Retrieval test accuracy: "
            f"{accuracy:.1f}%"
        )

    print("=" * 70)


if __name__ == "__main__":

    asyncio.run(main())