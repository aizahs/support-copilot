"""Retrieval Step: turns questions and chunks into embeddings and finds the most similar chunks to the question"""

"""Two retrievers with the same interface: search(question, k) -> [(chunk, score)]."""
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class TfidfRetriever:
    """Keyword-based retrieval. Runs offline, good baseline to compare against."""

    def __init__(self, chunks):
        self.chunks = chunks
        self.vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        self.matrix = self.vec.fit_transform([c["text"] for c in chunks])

    def search(self, question, k):
        scores = cosine_similarity(self.vec.transform([question]), self.matrix)[0]
        top = np.argsort(scores)[::-1][:k]
        return [(self.chunks[i], float(scores[i])) for i in top]


class GeminiRetriever:
    """Meaning-based retrieval using Gemini embeddings + cosine similarity."""

    def __init__(self, chunks, model):
        from google import genai
        self.client, self.model, self.chunks = genai.Client(), model, chunks
        self.matrix = self._embed([c["text"] for c in chunks])

    def _embed(self, texts):
        out = []
        for i in range(0, len(texts), 50):  # batch to stay under request limits
            res = self.client.models.embed_content(model=self.model, contents=texts[i:i + 50])
            out.extend(e.values for e in res.embeddings)
        m = np.array(out, dtype=float)
        return m / np.linalg.norm(m, axis=1, keepdims=True)

    def search(self, question, k):
        q = self._embed([question])[0]
        scores = self.matrix @ q
        top = np.argsort(scores)[::-1][:k]
        return [(self.chunks[i], float(scores[i])) for i in top]


def make_retriever(cfg, chunks):
    if cfg.retriever == "gemini":
        return GeminiRetriever(chunks, cfg.embed_model)
    return TfidfRetriever(chunks)
