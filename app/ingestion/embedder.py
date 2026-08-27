import httpx

from app.config import (
    OPENROUTER_API_KEY,
    EMBEDDING_MODEL,
)


OPENROUTER_EMBEDDINGS_URL = (
    "https://openrouter.ai/api/v1/embeddings"
)


async def embed_texts(
    texts: list[str],
) -> list[list[float]]:

    if not texts:
        return []

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": EMBEDDING_MODEL,
        "input": texts,
    }

    async with httpx.AsyncClient(timeout=90) as client:

        response = await client.post(
            OPENROUTER_EMBEDDINGS_URL,
            headers=headers,
            json=payload,
        )

        response.raise_for_status()

        data = response.json()

    # The API returns one embedding object
    # for each input text. Sorting by index
    # guarantees that vector i belongs to
    # input text i.
    items = sorted(
        data["data"],
        key=lambda item: item["index"],
    )

    return [
        item["embedding"]
        for item in items
    ]


async def embed_one(text: str) -> list[float]:

    embeddings = await embed_texts([text])

    return embeddings[0]