# Support Copilot

An AI support assistant that answers client questions about investing accounts (TFSAs, RRSPs, transfers)
from public help-centre articles, and **hands off to a human agent when it isn't confident**.

The interesting part is the evaluation: every answer is measured for accuracy, hallucinations,
and whether the assistant escalated when it should have.

## How it works
1. **Ingest:** help articles are split into overlapping chunks (`copilot/ingest.py`).
2. **Retrieve:** the question is matched to the most relevant chunks, with TF-IDF (keyword) or Gemini embeddings (meaning) (`copilot/retrieve.py`).
3. **Guardrail 1:** if the best match is weak, escalate to an agent instead of guessing.
4. **Answer:** the LLM answers *only* from the retrieved text and cites the source.
5. **Guardrail 2:** if the model says the context isn't enough, escalate.

## Quick start
```bash
pip install -r requirements.txt
python app.py --stub --demo        # offline test on fictional sample articles
export GEMINI_API_KEY=your_key     # free key from Google AI Studio
python app.py                      # real run on data/articles
```

## Adding articles
```bash
python fetch_articles.py   # downloads every URL in urls.txt into data/articles/
python add_article.py      # or paste one article manually: URL, title, text, then END
```
Each article becomes `data/articles/<title>.md` with its source URL at the top.

## Evaluation
1. Copy `eval/questions_template.csv` to `eval/questions.csv` and write ~100 realistic questions:
   about 80 answerable from your articles (with the correct answer and source) and about 20 that
   **should** be escalated (advice, account-specific, off-topic).
2. Run both arms (top-3 vs top-8 retrieved chunks) and grade them:
   ```bash
   python eval/run_eval.py --questions eval/questions.csv
   ```
3. **Hand-check** a sample of the `verdict` column in `eval/results.csv` and fix anything the LLM judge got wrong.
4. Report:
   ```bash
   python eval/report.py
   ```
   You get accuracy, hallucination rate, escalation precision/recall per arm, and a McNemar test
   saying whether the difference between arms is real or noise.

## Results
_Fill in after your run: accuracy, hallucination rate, escalation precision/recall, and what you changed because of it._
