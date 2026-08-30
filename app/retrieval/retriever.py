from app.config import QDRANT_COLLECTION
from app.database.qdrant_db import client


def retrieve(
    query_vector: list[float],
    top_k: int = 5,
    score_threshold: float = 0.05,
):
    """
    Retrieve relevant document chunks from Qdrant.

    Parameters
    ----------
    query_vector:
        The embedding vector of the user's question.

    top_k:
        Maximum number of chunks to retrieve.

    score_threshold:
        Minimum similarity score required for a chunk
        to be considered relevant.

    Returns
    -------
    A list of relevant Qdrant points.
    """

    # -----------------------------------------
    # Ask Qdrant for the most similar chunks.
    #
    # We still retrieve top_k candidates first.
    # -----------------------------------------

    results = client.query_points(
        collection_name=QDRANT_COLLECTION,
        query=query_vector,
        limit=top_k,
        with_payload=True,
    )

    # -----------------------------------------
    # Remove weak results.
    #
    # Qdrant returns a similarity score for
    # every result.
    # -----------------------------------------

    filtered_results = [
        point
        for point in results.points
        if point.score >= score_threshold
    ]

    return filtered_results
