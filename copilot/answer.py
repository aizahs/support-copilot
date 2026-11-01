"""The copilot: retrieve, decide whether to escalate, answer from sources only."""
from .ingest import build_chunks
from .retrieve import make_retriever
from .llm import generate

PROMPT = """You are a support assistant for an investing app.
Answer the client's question using ONLY the context below.
Keep it short and plain-language, and name the source article in brackets.
If the context does not clearly answer the question, reply with exactly: ESCALATE

CONTEXT:
{context}

QUESTION: {question}
ANSWER:"""

HANDOFF = "I'm not fully sure about that one, so let me connect you with an agent who can help."


class Copilot:
    def __init__(self, cfg):
        self.cfg = cfg
        self.retriever = make_retriever(cfg, build_chunks(cfg))

    def ask(self, question):
        hits = self.retriever.search(question, self.cfg.top_k)
        top_score = hits[0][1] if hits else 0.0
        sources = [c["source"] for c, _ in hits]

        # Guardrail 1: weak retrieval means we probably don't have the answer.
        if top_score < self.cfg.escalate_threshold:
            return {"answer": HANDOFF, "escalated": True, "reason": "low_retrieval",
                    "top_score": top_score, "sources": sources}

        context = "\n\n".join(f"[{c['source']}] {c['text']}" for c, _ in hits)
        reply = generate(PROMPT.format(context=context, question=question), self.cfg)

        # Guardrail 2: the model itself says the context isn't enough.
        if reply.strip().upper().startswith("ESCALATE"):
            return {"answer": HANDOFF, "escalated": True, "reason": "model_unsure",
                    "top_score": top_score, "sources": sources}
        return {"answer": reply, "escalated": False, "reason": "",
                "top_score": top_score, "sources": sources}
