from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, UploadFile, File, HTTPException

from app.schemas import AskRequest, AskResponse
from app.database.qdrant_db import (
    client,
    create_collection_if_needed,
)
from app.ingestion.loader import load_document
from app.ingestion.embedder import embed_one
from app.ingestion.chunker import chunk_text
from app.retrieval.retriever import retrieve
from app.generation.generator import generate_answer
from app.generation.prompt import build_rag_prompt
from app.ingestion.ingest import ingest_file


app = FastAPI(
    title="DocMind RAG",
    version="1.0.0",
)


@app.on_event("startup")
def startup():

    create_collection_if_needed()


@app.get("/health")
def health():

    return {
        "status": "ok",
        "service": "DocMind RAG",
    }

@app.post("/ingest")
async def ingest_document(
    file: UploadFile = File(...),
):

    # File types that our application supports
    allowed = {
        ".txt",
        ".pdf",
        ".docx",
    }

    filename = file.filename

    if not filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is missing.",
        )

    extension = Path(filename).suffix.lower()

    if extension not in allowed:
        raise HTTPException(
            status_code=400,
            detail="Only TXT, PDF and DOCX files are supported.",
        )

    upload_dir = Path("documents")
    upload_dir.mkdir(exist_ok=True)


    safe_name = Path(filename).name

    path = upload_dir / safe_name


    contents = await file.read()

    path.write_bytes(contents)

    try:

        result = await ingest_file(path)

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )

    return {
        "filename": safe_name,
        **result,
        "message": (
            "Document embedded and stored in Qdrant."
        ),
}


    # text = load_document(path)

    # if not text.strip():
    #     raise HTTPException(
    #         status_code=400,
    #         detail="No readable text was found.",
    #     )


    # chunks = chunk_text(text)


    # return {
    #     "filename": safe_name,
    #     "characters": len(text),
    #     "chunks": len(chunks),
    #     "message": "Document loaded and chunked.",
    # }



@app.post(
    "/ask",
    response_model=AskResponse,
)
async def ask(
    request: AskRequest,
):

    # -----------------------------------------
    # STEP 1
    # Get the user's question.
    # -----------------------------------------

    question = request.question.strip()

    # -----------------------------------------
    # STEP 2
    # Convert the question into an embedding.
    #
    # IMPORTANT:
    # We use the SAME embedding model that
    # was used for the documents.
    # -----------------------------------------

    query_vector = await embed_one(
        question
    )

    # -----------------------------------------
    # STEP 3
    # Search Qdrant.
    #
    # Qdrant compares the question vector
    # against our stored document vectors.
    # -----------------------------------------

    points = retrieve(
        query_vector=query_vector,
        top_k=5,
    )

    # -----------------------------------------
    # STEP 4
    # If nothing was retrieved, don't ask
    # the LLM to invent an answer.
    # -----------------------------------------

    if not points:

        return AskResponse(
            answer=(
                "I could not find any "
                "relevant information in "
                "the documents."
            ),
            sources=[],
        )

    # -----------------------------------------
    # STEP 5
    # AUGMENTATION
    #
    # Take the retrieved chunks and combine
    # them with the user's question.
    # -----------------------------------------

    prompt = build_rag_prompt(
        question,
        points,
    )

    # -----------------------------------------
    # STEP 6
    # Give the LLM strict instructions.
    # -----------------------------------------

    system_prompt = """
You are DocMind, a document question-answering
assistant.

Use the supplied document context.

Do not invent facts.

If the supplied context does not contain
enough information to answer the question,
say so clearly.

Cite claims using the source numbers
provided in the context.
"""

    # -----------------------------------------
    # STEP 7
    # Send the augmented prompt to
    # OpenRouter's selected free LLM.
    # -----------------------------------------

    answer = await generate_answer(
        system_prompt=system_prompt,
        user_prompt=prompt,
    )

    # -----------------------------------------
    # STEP 8
    # Return the retrieved sources along
    # with the generated answer.
    # -----------------------------------------

    sources = []

    for point in points:

        payload = point.payload or {}

        sources.append(
            {
                "source": payload.get(
                    "source",
                    "unknown",
                ),
                "chunk_index": payload.get(
                    "chunk_index",
                    -1,
                ),
                "score": point.score,
            }
        )

    return AskResponse(
        answer=answer,
        sources=sources,
    )