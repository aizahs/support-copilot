"""Run every labelled question through each config ("arm") and save results.

Saves after EVERY question and skips ones already done, so if you hit a rate
limit you can just run it again later and it picks up where it left off.

Usage:
  python eval/run_eval.py --questions eval/questions.csv
  python eval/run_eval.py --questions eval/questions.csv --no-judge   # grade by hand, half the API calls
  python eval/run_eval.py --questions eval/questions.csv --stub       # offline test
"""
import argparse, sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from copilot.config import Config
from copilot.answer import Copilot
from eval.grade import grade

ARMS = {
    "A_top3": dict(top_k=3),
    "B_top8": dict(top_k=8),
}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--questions", default="eval/questions.csv")
    ap.add_argument("--out", default="eval/results.csv")
    ap.add_argument("--articles", default="data/articles")
    ap.add_argument("--retriever", default="tfidf", choices=["tfidf", "gemini"])
    ap.add_argument("--stub", action="store_true", help="offline: fake LLM + simple grading")
    ap.add_argument("--no-judge", action="store_true", help="skip the LLM judge; fill in 'verdict' by hand")
    a = ap.parse_args()

    qs = pd.read_csv(a.questions).fillna("")
    out = Path(a.out)
    done = pd.read_csv(out) if out.exists() else pd.DataFrame(columns=["arm", "id"])
    done_keys = set(zip(done.arm, done.id))

    for arm, overrides in ARMS.items():
        cfg = Config(articles_dir=a.articles, retriever=a.retriever,
                     llm="stub" if a.stub else "gemini", **overrides)
        bot = Copilot(cfg)
        for _, q in qs.iterrows():
            if (arm, q["id"]) in done_keys:
                continue  # already answered in an earlier run
            r = bot.ask(q["question"])
            g = {"verdict": "", "escalation_correct": ""} if a.no_judge else grade(q, r, cfg)
            if a.no_judge and r["escalated"]:
                g = grade(q, r, cfg)  # escalations are graded without any API call
            row = {"arm": arm, "id": q["id"], "question": q["question"],
                   "expected_answer": q["expected_answer"],
                   "should_escalate": q["should_escalate"].strip().lower() == "yes",
                   "escalated": r["escalated"], "top_score": round(r["top_score"], 3),
                   "answer": r["answer"], "sources": ";".join(dict.fromkeys(r["sources"])), **g}
            pd.DataFrame([row]).to_csv(out, mode="a", header=not out.exists(), index=False)
            print(f"  {arm} {q['id']} -> {'escalated' if r['escalated'] else 'answered'} {g['verdict']}")
        print(f"finished {arm}")
    print(f"saved {out}. Spot-check the 'verdict' column, then run: python eval/report.py")
