"""Chat with the copilot in your terminal:  python app.py  (add --stub --demo to try it offline on sample data)"""
import sys
from copilot.config import Config
from copilot.answer import Copilot

if __name__ == "__main__":
    cfg = Config(llm="stub") if "--stub" in sys.argv else Config()
    if "--demo" in sys.argv:  # try it on the fictional sample articles
        cfg.articles_dir = "tests/sample_articles"
    bot = Copilot(cfg)
    print("Support Copilot ready. Type a question (or 'quit').")
    while (q := input("\nYou: ").strip()).lower() not in {"quit", "exit"}:
        r = bot.ask(q)
        tag = f"  (escalated: {r['reason']})" if r["escalated"] else f"  (sources: {', '.join(dict.fromkeys(r['sources']))})"
        print(f"Copilot: {r['answer']}{tag}")
