"""
Data Collection: downloads the webpages, strips headers and footers and saves as .md files
    pip install requests beautifulsoup4
    python fetch_articles.py
"""
import re, sys, time
from pathlib import Path
import requests
from bs4 import BeautifulSoup

OUT = Path("data/articles")
HEADERS = {"User-Agent": "Mozilla/5.0 (student research project)"}
JUNK = ["nav", "header", "footer", "script", "style", "noscript", "form", "aside", "button", "svg"]
JUNK_TEXT = re.compile(r"(report a problem|date modified|was this (article|page) helpful|share this page)", re.I)


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:60] or "article"


def main_content(soup):
    for sel in ["article .article-body", ".article-body", "main", "article", "[role=main]", "body"]:
        node = soup.select_one(sel)
        if node and len(node.get_text(strip=True)) > 200:
            return node
    return soup


def to_markdown(node):
    for tag in node.find_all(JUNK):
        tag.decompose()
    lines = []
    for el in node.find_all(["h1", "h2", "h3", "h4", "p", "li", "td"]):
        if el.find_parent(["li", "td"]) and el.name in ["p"]:
            continue  # avoid double-counting text inside list items
        text = " ".join(el.get_text(" ", strip=True).split())
        if not text or JUNK_TEXT.search(text):
            continue
        if el.name in ["h1", "h2", "h3", "h4"]:
            lines.append("#" * int(el.name[1]) + " " + text)
        elif el.name == "li":
            lines.append("- " + text)
        else:
            lines.append(text)
    md = "\n\n".join(lines)
    return re.sub(r"\n{3,}", "\n\n", md).strip()


def fetch(url):
    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    title = (soup.find("h1") or soup.title or soup).get_text(strip=True)
    body = to_markdown(main_content(soup))
    return title, body


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    urls = [u.strip() for u in Path("urls.txt").read_text().splitlines() if u.strip() and not u.startswith("#")]
    for url in urls:
        try:
            title, body = fetch(url)
            name = slugify(title)
            if (OUT / f"{name}.md").exists():
                name = f"{name}-{slugify(url.rstrip('/').split('/')[-1])}"
            (OUT / f"{name}.md").write_text(f"# {title}\n\nSource: {url}\n\n{body}\n", encoding="utf-8")
            print(f"saved  {name}.md  ({len(body):,} chars)")
        except Exception as e:
            print(f"FAILED {url}: {e}", file=sys.stderr)
        time.sleep(1)  # be polite to the websites
    print("\nDone. Open a few files in data/articles/ to check they look clean.")
