def build_rag_prompt(
    question: str,
    retrieved_chunks: list,
) -> str:

    context_parts = []

    for index, point in enumerate(
        retrieved_chunks,
        start=1,
    ):

        payload = point.payload or {}

        text = payload.get("text", "")
        source = payload.get("source", "unknown")

        context_parts.append(
            f"[SOURCE {index}: {source}]\n{text}"
        )

    context = "\n\n".join(context_parts)

    return f"""
Use ONLY the supplied context to answer the question.

If the answer cannot be found in the context,
say that the documents do not contain enough
information to answer the question.

Do not invent facts.

Cite supporting sources using [1], [2], etc.

CONTEXT:

{context}

QUESTION:

{question}
"""