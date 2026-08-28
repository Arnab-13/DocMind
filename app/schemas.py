from pydantic import BaseModel, Field


class AskRequest(BaseModel):

    question: str = Field(
        min_length=3,
        max_length=2000,
    )


class Source(BaseModel):

    source: str
    chunk_index: int
    score: float


class AskResponse(BaseModel):

    answer: str
    sources: list[Source]