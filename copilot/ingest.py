"""Chunking Step: 800 char chunks with 150 char overlap, for each .md or .txt article in data/articles/"""
from pathlib import Path


def load_articles(articles_dir):
    docs = []
    for path in sorted(Path(articles_dir).glob("*")):
        if path.suffix.lower() in {".md", ".txt"}:
            docs.append({"source": path.stem, "text": path.read_text(encoding="utf-8")})
    if not docs:
        raise FileNotFoundError(f"No .md or .txt articles found in {articles_dir}")
    return docs


def chunk_text(text, size, overlap):
    """Split on paragraphs first, then pack paragraphs into chunks of about `size` chars."""
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks, current = [], ""
    for p in paras:
        if current and len(current) + len(p) + 2 > size:
            chunks.append(current)
            current = current[-overlap:] + "\n\n" + p if overlap else p
        else:
            current = f"{current}\n\n{p}" if current else p
    if current:
        chunks.append(current)
    return chunks


def build_chunks(cfg):
    chunks = []
    for doc in load_articles(cfg.articles_dir):
        for i, c in enumerate(chunk_text(doc["text"], cfg.chunk_size, cfg.chunk_overlap)):
            chunks.append({"id": f"{doc['source']}#{i}", "source": doc["source"], "text": c})
    return chunks
