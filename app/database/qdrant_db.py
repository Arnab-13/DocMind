from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
)

from app.config import (
    QDRANT_URL,
    QDRANT_API_KEY,
    QDRANT_COLLECTION,
    EMBEDDING_DIMENSION,
)


client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
)


def create_collection_if_needed():

    collections = client.get_collections()

    existing_names = {
        collection.name
        for collection in collections.collections
    }

    if QDRANT_COLLECTION in existing_names:
        return

    client.create_collection(
        collection_name=QDRANT_COLLECTION,
        vectors_config=VectorParams(
            size=EMBEDDING_DIMENSION,
            distance=Distance.COSINE,
        ),
    )


def upsert_chunks(
    points: list[PointStruct],
):

    client.upsert(
        collection_name=QDRANT_COLLECTION,
        points=points,
    )

def upsert_points(
    points: list[PointStruct],
):
    """
    Store document vectors and their metadata
    inside Qdrant Cloud.
    """

    client.upsert(
        collection_name=QDRANT_COLLECTION,
        points=points,
    )