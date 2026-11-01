import pandas as pd
import matplotlib.pyplot as plt
from math import sqrt

df = pd.read_csv("eval/results.csv")

# Keep only questions that SHOULD be answered (not the escalation tests)
should_escalate = df["should_escalate"].astype(str).str.lower() == "true"
answerable = df[~should_escalate]

arms = ["A_top3", "B_top8"]
labels = ["Top-3 passages", "Top-8 passages"]
accuracies = []
margins = []

for arm in arms:
    rows = answerable[answerable["arm"] == arm]
    n = len(rows)
    p = (rows["verdict"] == "correct").mean()      # share answered correctly
    margin = 1.96 * sqrt(p * (1 - p) / n)          # 95% margin of error
    accuracies.append(p)
    margins.append(margin)
    print(arm, "n =", n, "accuracy =", round(p, 3), "+/-", round(margin, 3))

fig, ax = plt.subplots(figsize=(6, 4))
colors = ["#B8BEC6", "#2E7D5B"]                    # grey, then highlight the better one
ax.bar(labels, accuracies, yerr=margins, capsize=8, color=colors, width=0.5)

# Label each bar with its accuracy
for i, p in enumerate(accuracies):
    ax.text(i, p + margins[i] + 0.03, f"{p:.0%}", ha="center", fontsize=12, fontweight="bold")

ax.set_title("Accuracy on answerable questions (n = 24, with 95% error bars)", loc="left")
ax.set_ylabel("Accuracy")
ax.set_ylim(0, 1.1)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.savefig("eval/accuracy_chart.png", dpi=200, bbox_inches="tight")
print("saved eval/accuracy_chart.png")