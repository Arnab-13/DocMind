from rank_bm25 import BM25Okapi

from app.config import QDRANT_COLLECTION
from app.database.qdrant_db import (
    client,
    get_all_chunks,
)

import re


# -----------------------------------------
# SETTINGS
# -----------------------------------------

DEFAULT_TOP_K = 5

DENSE_SCORE_THRESHOLD = 0.05

RRF_K = 60

# -----------------------------------------
# BM25 CACHE
# -----------------------------------------

_bm25 = None
_bm25_points = []

def tokenize(text: str) -> list[str]:
    """
    Normalize text into simple keyword tokens
    for BM25 retrieval.
    """
    return re.findall(
        r"\b\w+\b",
        text.lower(),
    )

def rebuild_bm25_index():
    """
    Load all document chunks from Qdrant
    and rebuild the BM25 index.

    This should be called:
    - when the application starts
    - after a document is ingested
    """

    global _bm25
    global _bm25_points

    points = get_all_chunks()

    documents = []
    valid_points = []

    for point in points:

        payload = point.payload or {}

        text = payload.get("text")

        if not text:
            continue

        documents.append(text)
        valid_points.append(point)

    if not documents:

        _bm25 = None
        _bm25_points = []

        return

    tokenized_documents = [
        tokenize(document)
        for document in documents
    ]

    _bm25 = BM25Okapi(
        tokenized_documents
    )

    _bm25_points = valid_points

# -----------------------------------------
# DENSE SEARCH
# -----------------------------------------

def dense_retrieve(
    query_vector: list[float],
    top_k: int = DEFAULT_TOP_K,
    score_threshold: float = DENSE_SCORE_THRESHOLD,
):
    """
    Retrieve chunks using embedding similarity.

    This is the original DocMind retrieval
    method that was already working.
    """

    results = client.query_points(
        collection_name=QDRANT_COLLECTION,
        query=query_vector,
        limit=top_k,
        with_payload=True,
    )

    filtered_results = [
        point
        for point in results.points
        if point.score >= score_threshold
    ]

    return filtered_results


# -----------------------------------------
# BM25 SEARCH
# -----------------------------------------

def bm25_retrieve(
    question: str,
    top_k: int = DEFAULT_TOP_K,
):
    """
    Retrieve chunks using the cached BM25 index.
    """

    if _bm25 is None:
        rebuild_bm25_index()

    if _bm25 is None:
        return []

    tokenized_question = tokenize(
        question
    )

    scores = _bm25.get_scores(
        tokenized_question
    )

    ranked_indexes = sorted(
        range(len(scores)),
        key=lambda index: scores[index],
        reverse=True,
    )

    results = []

    for index in ranked_indexes[:top_k]:

        # Ignore chunks with no keyword match.
        if scores[index] <= 0:
            continue

        point = _bm25_points[index]

        point = point.model_copy(
            update={
                "score": float(scores[index])
            }
        )

        results.append(point)

    return results


# -----------------------------------------
# RECIPROCAL RANK FUSION
# -----------------------------------------

def reciprocal_rank_fusion(
    dense_results,
    keyword_results,
    top_k: int = DEFAULT_TOP_K,
):
    """
    Combine dense-search and BM25 rankings using
    Reciprocal Rank Fusion (RRF).

    Results that appear in BOTH retrieval methods
    receive an additional boost because they have
    stronger evidence of relevance.
    """

    fused_scores = {}
    point_lookup = {}
    retrieval_sources = {}

    # Dense-search rankings
    for rank, point in enumerate(dense_results, start=1):
        point_id = str(point.id)

        fused_scores[point_id] = (
            fused_scores.get(point_id, 0)
            + 1 / (RRF_K + rank)
        )

        point_lookup[point_id] = point
        retrieval_sources.setdefault(point_id, set()).add("dense")

    # BM25 rankings
    for rank, point in enumerate(keyword_results, start=1):
        point_id = str(point.id)

        fused_scores[point_id] = (
            fused_scores.get(point_id, 0)
            + 1 / (RRF_K + rank)
        )

        point_lookup[point_id] = point
        retrieval_sources.setdefault(point_id, set()).add("bm25")

    # Give documents found by BOTH methods a boost.
    for point_id, sources in retrieval_sources.items():
        if len(sources) == 2:
            fused_scores[point_id] *= 1.5

    # Sort by final fused score.
    ranked_ids = sorted(
        fused_scores.keys(),
        key=lambda point_id: fused_scores[point_id],
        reverse=True,
    )

    final_results = []

    for point_id in ranked_ids[:top_k]:
        point = point_lookup[point_id]

        point = point.model_copy(
            update={"score": fused_scores[point_id]}
        )

        final_results.append(point)

    return final_results

# -----------------------------------------
# HYBRID RETRIEVAL
# -----------------------------------------

def hybrid_retrieve(
    question: str,
    query_vector: list[float],
    top_k: int = DEFAULT_TOP_K,
):
    """
    Perform hybrid retrieval.

    Combines:
        1. Dense semantic search
        2. BM25 keyword search
        3. Reciprocal Rank Fusion

    A small final threshold removes very weak
    hybrid matches before sending them to the LLM.
    """

    dense_results = dense_retrieve(
        query_vector=query_vector,
        top_k=top_k,
    )

    keyword_results = bm25_retrieve(
        question=question,
        top_k=top_k,
    )

    results = reciprocal_rank_fusion(
        dense_results=dense_results,
        keyword_results=keyword_results,
        top_k=top_k,
    )

    # RRF scores are normally around 0.01 - 0.03.
    # Keep only results that have meaningful
    # support from the retrieval methods.
    HYBRID_SCORE_THRESHOLD = 0.02

    filtered_results = [
        point
        for point in results
        if point.score >= HYBRID_SCORE_THRESHOLD
    ]

    return filtered_results