"""All the knobs you'll want to tweak and compare in experiments."""
import os
from dataclasses import dataclass

try:  # load GEMINI_API_KEY etc. from a .env file in the project folder, if there is one
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


@dataclass
class Config:
    articles_dir: str = "data/articles"
    chunk_size: int = 800          # characters per chunk
    chunk_overlap: int = 150       # characters shared between neighbouring chunks
    top_k: int = 3                 # how many chunks to give the LLM
    escalate_threshold: float = 0.08  # below this retrieval score, hand off to an agent
    retriever: str = "tfidf"       # "tfidf" (offline) or "gemini" (embeddings)
    llm: str = "gemini"            # "gemini" or "stub" (offline testing)
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    embed_model: str = os.getenv("GEMINI_EMBED_MODEL", "gemini-embedding-001")
