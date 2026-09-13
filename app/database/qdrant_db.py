from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    PayloadSchemaType,
)

from app.config import (
    QDRANT_URL,
    QDRANT_API_KEY,
    QDRANT_COLLECTION,
    EMBEDDING_DIMENSION,
)


# -----------------------------------------
# QDRANT CLOUD CONNECTION
# -----------------------------------------

client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
)


# -----------------------------------------
# CREATE COLLECTION
# -----------------------------------------

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

def create_document_index():
    """
    Create a keyword index on document_id.

    This allows Qdrant to efficiently find all
    chunks belonging to a particular document.
    """

    client.create_payload_index(
        collection_name=QDRANT_COLLECTION,
        field_name="document_id",
        field_schema=PayloadSchemaType.KEYWORD,
    )


# -----------------------------------------
# DELETE EXISTING DOCUMENT
# -----------------------------------------

def delete_document(
    document_id: str,
):
    """
    Delete every vector belonging to
    a particular document.

    We identify the vectors using the
    document_id stored in their payload.
    """

    client.delete(
        collection_name=QDRANT_COLLECTION,

        points_selector=Filter(
            must=[
                FieldCondition(
                    key="document_id",
                    match=MatchValue(
                        value=document_id
                    ),
                )
            ]
        ),
    )


# -----------------------------------------
# STORE DOCUMENT VECTORS
# -----------------------------------------

def upsert_points(
    points: list[PointStruct],
):
    """
    Store document vectors and metadata
    inside Qdrant Cloud.
    """

    client.upsert(
        collection_name=QDRANT_COLLECTION,
        points=points,
    )


# -----------------------------------------
# GET ALL STORED CHUNKS
# -----------------------------------------

def get_all_chunks():
    """
    Retrieve all stored document chunks from Qdrant.

    This is used by the local BM25 keyword
    search component of hybrid retrieval.

    We only retrieve the payload because BM25
    does not need the embedding vectors.
    """

    all_points = []

    offset = None

    while True:

        points, offset = client.scroll(
            collection_name=QDRANT_COLLECTION,
            limit=100,
            offset=offset,
            with_payload=True,
            with_vectors=False,
        )

        all_points.extend(points)

        if offset is None:
            break

    return all_points