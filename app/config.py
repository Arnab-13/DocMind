import os
from dotenv import load_dotenv

load_dotenv()


def required_env(name: str) -> str:
    value = os.getenv(name)

    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")

    return value


OPENROUTER_API_KEY = required_env("OPENROUTER_API_KEY")
QDRANT_URL = required_env("QDRANT_URL")
QDRANT_API_KEY = required_env("QDRANT_API_KEY")

LLM_MODEL = os.getenv("LLM_MODEL", "openrouter/free")

QDRANT_COLLECTION = os.getenv(
    "QDRANT_COLLECTION",
    "docmind_documents",
)

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2",
)

EMBEDDING_DIMENSION = int(
    os.getenv("EMBEDDING_DIMENSION", "384")
)