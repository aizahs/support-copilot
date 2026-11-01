"""For each test question, show the expected answer next to the closest
sentences from its source article, so you can verify it quickly."""
import re
import pandas as pd
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

qs = pd.read_csv("eval/questions.csv").fillna("")

for _, q in qs.iterrows():
    if q["should_escalate"] == "yes":
        continue  # no answer to check for these
    path = Path("data/articles") / f"{q['source_article']}.md"
    print("=" * 80)
    print(f"{q['id']}: {q['question']}")
    print(f"EXPECTED: {q['expected_answer']}")
    if not path.exists():
        print(f"!! Article not found: {path}")
        continue
    # split the article into sentences
    text = path.read_text(encoding="utf-8")
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", text) if len(s.strip()) > 30]
    # score each sentence against the expected answer
    vec = TfidfVectorizer(stop_words="english").fit(sentences + [q["expected_answer"]])
    scores = cosine_similarity(vec.transform([q["expected_answer"]]), vec.transform(sentences))[0]
    print("CLOSEST SENTENCES IN ARTICLE:")
    for i in scores.argsort()[::-1][:3]:
        print(f"  ({scores[i]:.2f}) {sentences[i]}")