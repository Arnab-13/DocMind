from app.config import QDRANT_COLLECTION
from app.database.qdrant_db import client


def retrieve(
    query_vector: list[float],
    top_k: int = 5,
):

    results = client.query_points(
        collection_name=QDRANT_COLLECTION,
        query=query_vector,
        limit=top_k,
        with_payload=True,
    )

    return results.points