import asyncio

from app.ingestion.embedder import embed_one


async def main():

    text = (
        "Retrieval augmented generation "
        "combines information retrieval "
        "with language models."
    )

    vector = await embed_one(text)

    print("Vector dimension:", len(vector))
    print("First five values:", vector[:5])


if __name__ == "__main__":
    asyncio.run(main())