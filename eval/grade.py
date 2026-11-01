"""Label each answer as correct / incorrect / hallucination / escalated.

Real runs use an LLM judge (Gemini) comparing against your expected answer.
ALWAYS spot-check a sample by hand and fix the 'verdict' column if the judge is wrong:
that manual check is what makes your numbers trustworthy.
"""
from copilot.llm import generate

JUDGE = """You are grading a support assistant. Compare the ANSWER to the EXPECTED answer.
Reply with exactly one word:
CORRECT - same key facts as expected
INCORRECT - misses or gets wrong the key facts, but invents nothing
HALLUCINATION - states facts that are not in the expected answer or the sources

QUESTION: {q}
EXPECTED: {expected}
ANSWER: {answer}
VERDICT:"""


def grade(q, r, cfg):
    should = q["should_escalate"].strip().lower() == "yes"
    if r["escalated"]:
        return {"verdict": "escalated", "escalation_correct": should}
    if should:  # answered something it should have handed off
        return {"verdict": "should_have_escalated", "escalation_correct": False}
    if cfg.llm == "stub":
        hit = q["source_article"] and q["source_article"] in r["sources"]
        return {"verdict": "correct" if hit else "incorrect", "escalation_correct": True}
    v = generate(JUDGE.format(q=q["question"], expected=q["expected_answer"], answer=r["answer"]), cfg)
    v = v.strip().split()[0].lower() if v.strip() else "incorrect"
    v = v if v in {"correct", "incorrect", "hallucination"} else "incorrect"
    return {"verdict": v, "escalation_correct": True}
