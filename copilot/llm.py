"""LLM call. 'stub' mode lets you test the whole pipeline without an API key."""
import time


def generate(prompt, cfg, retries=5):
    if cfg.llm == "stub":
        context = prompt.split("CONTEXT:", 1)[-1].split("QUESTION:", 1)[0].strip()
        first_block = context.split("] ", 1)[-1] if context.startswith("[") else ""
        lines = [l for l in first_block.splitlines() if l.strip() and not l.startswith("#")]
        text = " ".join(lines)
        return (text.split(". ")[0].rstrip(".") + ".") if text else "ESCALATE"
    from google import genai
    client = genai.Client()  # reads GEMINI_API_KEY from your environment
    wait = 5
    for attempt in range(1, retries + 1):
        try:
            reply = client.models.generate_content(model=cfg.gemini_model, contents=prompt).text
            time.sleep(4)  # free tier allows only a few requests per minute
            return (reply or "").strip()
        except Exception as e:
            msg = str(e)
            if "PerDay" in msg or "per day" in msg:
                raise SystemExit(f"\nDaily free quota used up for {cfg.gemini_model}. "
                                 "Switch models (export GEMINI_MODEL=...) or try again tomorrow; "
                                 "your progress so far is saved.")
            busy = any(c in msg for c in ["503", "429", "UNAVAILABLE", "RESOURCE_EXHAUSTED"])
            if not busy or attempt == retries:
                raise
            print(f"  Gemini busy (attempt {attempt}/{retries}), retrying in {wait}s...")
            time.sleep(wait)
            wait *= 2  # exponential backoff: 5s, 10s, 20s, 40s
