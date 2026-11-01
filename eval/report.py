"""Summarize results per arm and test whether the difference between arms is real.

Usage: python eval/report.py --results eval/results.csv
"""
import argparse
import pandas as pd
from scipy.stats import binomtest


def summarize(df):
    answerable = df[~df.should_escalate]
    out = {
        "questions": len(df),
        "accuracy (answerable)": (answerable.verdict == "correct").mean(),
        "hallucination rate (answered)": (df[~df.escalated].verdict.isin(["hallucination", "should_have_escalated"])).mean()
            if (~df.escalated).any() else 0.0,
        "escalation precision": (df[df.escalated].should_escalate).mean() if df.escalated.any() else float("nan"),
        "escalation recall": (df[df.should_escalate].escalated).mean() if df.should_escalate.any() else float("nan"),
    }
    return {k: (round(v, 3) if isinstance(v, float) else v) for k, v in out.items()}


def mcnemar(df, a, b):
    """Paired test on the same questions: did arm B fix more than it broke?"""
    pa = df[df.arm == a].set_index("id").verdict.eq("correct")
    pb = df[df.arm == b].set_index("id").verdict.eq("correct")
    pa, pb = pa.align(pb, join="inner")
    b_only, a_only = int((~pa & pb).sum()), int((pa & ~pb).sum())
    n = a_only + b_only
    p = binomtest(b_only, n, 0.5).pvalue if n else 1.0
    return a_only, b_only, p


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="eval/results.csv")
    df = pd.read_csv(ap.parse_args().results)
    arms = list(dict.fromkeys(df.arm))
    for arm in arms:
        print(f"\n== {arm} ==")
        for k, v in summarize(df[df.arm == arm]).items():
            print(f"  {k:32s} {v}")
    if len(arms) >= 2:
        a_only, b_only, p = mcnemar(df, arms[0], arms[1])
        print(f"\n{arms[0]} right & {arms[1]} wrong: {a_only} | {arms[1]} right & {arms[0]} wrong: {b_only}")
        print(f"McNemar p-value: {p:.3f}  ->  {'likely a real difference' if p < 0.05 else 'not enough evidence yet (could be noise)'}")
