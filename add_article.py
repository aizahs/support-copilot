"""Turn a copied help article into a clean .md file in data/articles/.

Run:  python add_article.py
Then: paste the URL, the title, and the article text. Type END on its own line when done.
"""
import re
from pathlib import Path


def slugify(title):
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:60]


def clean(text):
    lines = [l.rstrip() for l in text.splitlines()]
    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)  # collapse big gaps into one blank line
    return text.strip()


if __name__ == "__main__":
    url = input("Article URL: ").strip()
    title = input("Article title: ").strip()
    print("Paste the article text, then type END on its own line:")
    body = []
    while (line := input()) != "END":
        body.append(line)
    out_dir = Path("data/articles")
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{slugify(title)}.md"
    path.write_text(f"# {title}\n\nSource: {url}\n\n{clean(chr(10).join(body))}\n", encoding="utf-8")
    print(f"Saved {path}")
