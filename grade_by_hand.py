"""Grade the answered questions yourself, one at a time.

Run from the main project folder:  python grade_by_hand.py
For each answer type:  c = correct,  i = incorrect,  h = hallucination,  s = skip for now
Your grades are saved into eval/results.csv as you go.
"""
import pandas as pd

PATH = "eval/results.csv"
df = pd.read_csv(PATH).fillna("")
todo = df[(df.verdict == "") & (~df.escalated.astype(bool))]
labels = {"c": "correct", "i": "incorrect", "h": "hallucination"}

print(f"{len(todo)} answers to grade.\n")
for idx, row in todo.iterrows():
    print("=" * 70)
    print(f"[{row.arm}] {row.id}: {row.question}")
    print(f"\nEXPECTED: {row.expected_answer}")
    print(f"\nCOPILOT:  {row.answer}\n")
    choice = ""
    while choice not in {"c", "i", "h", "s", "q"}:
        choice = input("c / i / h / s(kip) / q(uit): ").strip().lower()
    if choice == "q":
        break
    if choice == "s":
        continue
    df.loc[idx, "verdict"] = labels[choice]
    df.loc[idx, "escalation_correct"] = True
    df.to_csv(PATH, index=False)  # save after every grade

left = ((df.verdict == "") & (~df.escalated.astype(bool))).sum()
print(f"\nSaved. {left} left to grade." + ("" if left else " All done! Now run: python eval/report.py"))
