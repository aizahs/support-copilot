"""Support Copilot web app.

Run:  streamlit run streamlit_app.py
Tabs:
  Ask      - chat with the copilot, see its sources and when it hands off
  Results  - the evaluation results from eval/results.csv
"""
import html
import os
from math import sqrt
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

from copilot.config import Config
from copilot.answer import Copilot

st.set_page_config(page_title="Support Copilot", page_icon="💬", layout="centered")

# ---------- Look and feel ----------
NAVY = "#1B2A4A"
YELLOW = "#F5C842"
MUTED = "#6B7280"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif&family=Manrope:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500&display=swap');

html, body, [class*="css"], .stMarkdown, p, li, input, textarea, button {
  font-family: 'Manrope', sans-serif !important;
}
.stApp {
  background: radial-gradient(circle at 50% -10%, #E7ECF7 0%, #F6F7FB 45%, #F6F7FB 100%);
}
#MainMenu, footer, header {visibility: hidden;}
.block-container {padding-top: 2.5rem; max-width: 820px;}

/* Hero */
.eyebrow {
  font-family: 'IBM Plex Mono', monospace; font-size: 12px; letter-spacing: 2px;
  text-transform: uppercase; color: #3B4C78; text-align: center;
  background: #FFFFFF; border: 1px solid #E3E7F0; border-radius: 999px;
  padding: 6px 14px; width: fit-content; margin: 0 auto 18px auto;
}
.hero-title {
  font-family: 'Instrument Serif', serif !important; font-size: 68px !important; line-height: 1.02 !important;
  color: #14182B; text-align: center; margin: 0 0 22px 0 !important; font-weight: 400 !important; padding: 0 !important;
}
.hero-sub {display: flex; justify-content: center; margin: 4px 0 26px 0;}
.hero-sub span {color: #4B5563; text-align: center; font-size: 17px; max-width: 560px; line-height: 1.5;}
div[data-testid="stButtonGroup"] {display: flex; justify-content: center;}
div[data-testid="stButtonGroup"] button {border-radius: 999px !important; border: 1px solid #D9DEEA !important;
  background: #FFFFFF; margin: 0 3px; box-shadow: 0 4px 14px rgba(27, 42, 74, 0.06);}
div[data-testid="stButtonGroup"] button[kind="segmented_controlActive"],
div[data-testid="stButtonGroup"] button[aria-checked="true"] {background: #1B2A4A !important; border-color: #1B2A4A !important;}
div[data-testid="stButtonGroup"] button[kind="segmented_controlActive"] p,
div[data-testid="stButtonGroup"] button[aria-checked="true"] p {color: #FFFFFF !important;}

/* Pill buttons (example questions) */
.stButton > button {
  border-radius: 999px; border: 1px solid #D9DEEA; background: #FFFFFF; color: #14182B;
  font-weight: 500; font-size: 14px; padding: 10px 16px;
  box-shadow: 0 4px 14px rgba(27, 42, 74, 0.06); transition: all .15s ease;
}
.stButton > button:hover {background: #1B2A4A; color: #FFFFFF; border-color: #1B2A4A;}

/* Tabs */
.stTabs [role="tablist"] {gap: 6px; background: #FFFFFF; border-radius: 999px; padding: 5px;
  width: fit-content; margin: 0 auto 14px auto; border: 1px solid #E3E7F0; border-bottom: 1px solid #E3E7F0;}
.stTabs button[role="tab"] {border-radius: 999px; padding: 8px 24px; height: auto; background: transparent; border: none;}
.stTabs button[role="tab"][aria-selected="true"] {background: #1B2A4A;}
.stTabs button[role="tab"][aria-selected="true"] p {color: #FFFFFF !important;}
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] {display: none !important;}

/* Chat cards */
.msg-user {
  background: #1B2A4A; color: #FFFFFF; padding: 14px 18px; border-radius: 20px 20px 6px 20px;
  margin: 18px 0 10px auto; width: fit-content; max-width: 80%; font-size: 15px;
  box-shadow: 0 8px 24px rgba(27, 42, 74, 0.18);
}
.msg-bot {
  background: #FFFFFF; border: 1px solid #E8EBF2; padding: 18px 20px; border-radius: 20px 20px 20px 6px;
  max-width: 88%; font-size: 15px; color: #14182B; line-height: 1.55;
  box-shadow: 0 12px 32px rgba(27, 42, 74, 0.08);
}
.meta {display: flex; flex-wrap: wrap; gap: 6px; margin-top: 12px; align-items: center;}
.chip {
  font-family: 'IBM Plex Mono', monospace; font-size: 11px; color: #3B4C78; background: #EEF1F8;
  border-radius: 999px; padding: 4px 10px;
}
.handoff {
  display: flex; gap: 10px; align-items: center; margin-top: 12px; padding: 10px 12px;
  background: #FFF8E1; border-radius: 12px; font-size: 13px; color: #5B4A12;
}
.handoff .dot {background: #F5C842; border-radius: 8px; width: 28px; height: 28px; display: grid;
  place-items: center; font-size: 15px;}

/* Chat input */
[data-testid="stChatInput"], [data-testid="stChatInput"] > div {border-radius: 999px !important;
  border-color: #D9DEEA !important; background: #FFFFFF !important;}
[data-testid="stChatInput"] {box-shadow: 0 10px 30px rgba(27, 42, 74, 0.08);}
[data-testid="stChatInput"] textarea {padding-left: 10px;}

/* Results cards */
.stat-row {display: flex; gap: 14px; margin: 8px 0 22px 0;}
.stat {
  flex: 1; background: #FFFFFF; border: 1px solid #E8EBF2; border-radius: 20px; padding: 20px 22px;
  box-shadow: 0 12px 32px rgba(27, 42, 74, 0.07);
}
.stat .label {font-family: 'IBM Plex Mono', monospace; font-size: 11px; letter-spacing: 1.5px;
  text-transform: uppercase; color: #6B7280;}
.stat .value {font-family: 'Instrument Serif', serif; font-size: 52px; color: #14182B; line-height: 1.1;}
.stat .note {font-size: 13px; color: #6B7280;}
.section-title {font-family: 'Instrument Serif', serif; font-size: 34px; color: #14182B; margin: 18px 0 4px 0;}
</style>
""", unsafe_allow_html=True)

# ---------- Sidebar: settings ----------
st.sidebar.header("Settings")
top_k = st.sidebar.radio("Passages to retrieve", [3, 8], index=1,
                         help="How many article passages the assistant reads before answering.")
threshold = st.sidebar.slider("Escalation threshold", 0.0, 0.3, 0.08, 0.01,
                              help="Below this retrieval score, the assistant hands off to a human.")
use_stub = not os.getenv("GEMINI_API_KEY")
if use_stub:
    st.sidebar.warning("No GEMINI_API_KEY found, so answers use offline demo mode.")


@st.cache_resource(show_spinner="Loading articles...")
def load_bot(top_k, threshold, use_stub):
    cfg = Config(top_k=top_k, escalate_threshold=threshold, llm="stub" if use_stub else "gemini")
    return Copilot(cfg)


bot = load_bot(top_k, threshold, use_stub)

# ---------- Hero ----------
st.markdown('<div class="eyebrow">AI support assistant</div>', unsafe_allow_html=True)
st.markdown('<h1 class="hero-title">Clear answers about<br>your TFSA and RRSP</h1>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub"><span>Answers come only from trusted CRA and Wealthsimple articles. '
            'When it isn’t sure, it hands you to a human.</span></div>', unsafe_allow_html=True)

_, mid, _ = st.columns([1, 1, 1])
with mid:
    view = st.segmented_control("View", ["Ask", "Results"], default="Ask",
                                label_visibility="collapsed", width="stretch") or "Ask"

# ---------- View 1: Ask ----------
if view == "Ask":
    if "history" not in st.session_state:
        st.session_state.history = []

    examples = ["Can I re-contribute to my TFSA?",
                "Are RRSP contributions deductible?",
                "Which ETFs should I buy?"]
    cols = st.columns(len(examples))
    clicked = None
    for col, ex in zip(cols, examples):
        if col.button(ex, width="stretch"):
            clicked = ex

    for turn in st.session_state.history:
        r = turn["r"]
        st.markdown(f'<div class="msg-user">{html.escape(turn["q"])}</div>', unsafe_allow_html=True)
        if r["escalated"]:
            why = "weak match in the articles" if r["reason"] == "low_retrieval" else "the model wasn’t confident"
            extra = (f'<div class="handoff"><div class="dot">👤</div>'
                     f'<div><b>Handed off to a human</b><br>Reason: {why}</div></div>')
        else:
            retrieved = list(dict.fromkeys(r["sources"]))
            cited = [s for s in retrieved if s in r["answer"]]  # sources the answer names in [brackets]
            shown = cited or retrieved[:1]                        # none named: show the top match
            chips = "".join(f'<span class="chip">{html.escape(s)}</span>' for s in shown)
            extra = f'<div class="meta">{chips}</div>'
        score = f'<div class="meta"><span class="chip">retrieval score {r["top_score"]:.3f}</span></div>'
        answer = html.escape(r["answer"]).replace("\n", "<br>")
        st.markdown(f'<div class="msg-bot">{answer}{extra}{score}</div>', unsafe_allow_html=True)

    question = st.chat_input("Ask about TFSAs or RRSPs") or clicked
    if question:
        with st.spinner("Thinking..."):
            r = bot.ask(question)
        st.session_state.history.append({"q": question, "r": r})
        st.rerun()

# ---------- View 2: Results ----------
else:
    path = Path("eval/results.csv")
    if not path.exists():
        st.info("No results yet. Run: python eval/run_eval.py")
    else:
        df = pd.read_csv(path)
        df["should_escalate"] = df["should_escalate"].astype(str).str.lower() == "true"
        df["escalated"] = df["escalated"].astype(str).str.lower() == "true"
        arms = list(dict.fromkeys(df["arm"]))

        st.markdown('<div class="section-title">Accuracy on answerable questions</div>', unsafe_allow_html=True)
        cards = []
        for arm in arms:
            ans = df[(df["arm"] == arm) & ~df["should_escalate"]]
            p = (ans["verdict"] == "correct").mean() if len(ans) else 0
            margin = 1.96 * sqrt(p * (1 - p) / len(ans)) if len(ans) else 0
            cards.append(f'<div class="stat"><div class="label">{html.escape(arm)}</div>'
                         f'<div class="value">{int(p * 100 + 0.5)}%</div></div>')
        halluc = int((df["verdict"] == "hallucination").sum())
        cards.append(f'<div class="stat"><div class="label">Hallucinations</div>'
                     f'<div class="value">{halluc}</div><div class="note">across all setups</div></div>')
        st.markdown(f'<div class="stat-row">{"".join(cards)}</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-title">What happened to every question</div>', unsafe_allow_html=True)

        def outcome(row):
            if row["escalated"]:
                return "Escalated correctly" if row["should_escalate"] else "Escalated unnecessarily"
            if row["should_escalate"]:
                return "Missed escalation"
            return {"correct": "Answered correctly", "hallucination": "Hallucinated"}.get(
                str(row["verdict"]), "Answered incorrectly")

        df["outcome"] = df.apply(outcome, axis=1)
        order = ["Answered correctly", "Escalated correctly", "Escalated unnecessarily",
                 "Answered incorrectly", "Missed escalation", "Hallucinated"]
        colors = [NAVY, "#8A9BC4", YELLOW, "#E39B5B", "#D9534F", "#7A1F1F"]
        counts = df.groupby(["arm", "outcome"]).size().reset_index(name="questions")
        counts["rank"] = counts["outcome"].map({o: i for i, o in enumerate(order)})

        chart = (alt.Chart(counts).mark_bar(cornerRadius=6)
                 .encode(x=alt.X("questions:Q", stack="zero", title="Questions"),
                         y=alt.Y("arm:N", title=None, sort=arms),
                         color=alt.Color("outcome:N", scale=alt.Scale(domain=order, range=colors),
                                         legend=alt.Legend(orient="bottom", title=None, columns=3)),
                         order=alt.Order("rank:Q"),
                         tooltip=["arm", "outcome", "questions"])
                 .properties(height=alt.Step(64))
                 .configure_view(stroke=None)
                 .configure_axis(grid=False, labelFont="Manrope, sans-serif", titleFont="Manrope, sans-serif", labelFontSize=13)
                 .configure_legend(labelFont="Manrope, sans-serif", labelFontSize=12))
        st.altair_chart(chart, width="stretch")