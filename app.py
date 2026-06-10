"""
app.py — "Ask Priyanshu's AI" : a premium, single-page AI portfolio experience.

Architecture:
  - A heavy custom-CSS design system injected once (dark, glassmorphic, Inter +
    Space Grotesk, gradient mesh background) that hides all default Streamlit chrome.
  - A multi-section landing rendered as styled HTML via st.markdown: animated hero
    with a role-rotator + live availability pill, an animated KPI band, project
    CASE-STUDY cards (Problem -> Approach -> Impact), an experience timeline, and a
    skills system.
  - The RAG chat (rag.py) stays as the native, functional centerpiece, restyled to
    match the design language.

No extra dependencies. Runs on Streamlit Community Cloud.
Author: Priyanshu Pandey
"""

import streamlit as st
from rag import load_chunks, build_retriever, answer_question

# ----------------------------- CONFIG / CONSTANTS -----------------------------
GITHUB   = "https://github.com/priyanshupandey07"
LINKEDIN = "https://linkedin.com/in/priyanshu-pandey-007951262"
EMAIL    = "pri090204@gmail.com"
PHONE    = "+91-8882281544"
RESUME_URL = "https://github.com/priyanshupandey07/ask-priyanshu/blob/main/PRIYAN_1.PDF"
st.set_page_config(page_title="Priyanshu Pandey — AI / LLM Engineer",
                   page_icon="✦", layout="wide", initial_sidebar_state="collapsed")

# ----------------------------- DESIGN SYSTEM (CSS) ----------------------------
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

:root{
  --bg:#080b14; --bg2:#0d1220; --card:rgba(255,255,255,.04);
  --line:rgba(255,255,255,.09); --line2:rgba(255,255,255,.14);
  --txt:#e8ecf4; --muted:#8b95ad; --faint:#5b647c;
  --a1:#6d6bff; --a2:#a855f7; --a3:#22d3ee; --ok:#34d399;
}
/* hide streamlit chrome */
#MainMenu, header[data-testid="stHeader"], footer, .stDeployButton,
[data-testid="stToolbar"], [data-testid="stDecoration"]{display:none!important;}
[data-testid="stAppViewContainer"]{background:var(--bg);}
.block-container{padding:0 1rem 4rem!important; max-width:1080px!important;}
html,body,[class*="css"]{font-family:'Inter',sans-serif; color:var(--txt);}

/* animated gradient-mesh backdrop */
[data-testid="stAppViewContainer"]::before{
  content:""; position:fixed; inset:0; z-index:0; pointer-events:none;
  background:
    radial-gradient(60% 50% at 15% 0%, rgba(109,107,255,.18), transparent 60%),
    radial-gradient(55% 45% at 95% 10%, rgba(168,85,247,.16), transparent 60%),
    radial-gradient(45% 40% at 50% 100%, rgba(34,211,238,.10), transparent 60%),
    var(--bg);
}
.main .block-container{position:relative; z-index:1;}

/* entrance animation */
@keyframes rise{from{opacity:0; transform:translateY(18px)} to{opacity:1; transform:none}}
@keyframes pop{0%{opacity:0; transform:scale(.8)} 60%{transform:scale(1.05)} 100%{opacity:1; transform:scale(1)}}
@keyframes float{0%,100%{transform:translateY(0)} 50%{transform:translateY(-8px)}}
@keyframes pulse{0%,100%{opacity:1; box-shadow:0 0 0 0 rgba(52,211,153,.5)} 50%{opacity:.7; box-shadow:0 0 0 6px rgba(52,211,153,0)}}
@keyframes slide{0%,18%{transform:translateY(0)} 25%,43%{transform:translateY(-100%)} 50%,68%{transform:translateY(-200%)} 75%,93%{transform:translateY(-300%)} 100%{transform:translateY(-400%)}}
.reveal{opacity:0; animation:rise .7s cubic-bezier(.2,.7,.2,1) forwards;}

/* HERO */
.hero{padding:64px 0 28px; text-align:center;}
.avatar{width:74px;height:74px;border-radius:20px;margin:0 auto 22px;
  display:flex;align-items:center;justify-content:center;font-family:'Space Grotesk';
  font-weight:700;font-size:30px;color:#fff;
  background:linear-gradient(135deg,var(--a1),var(--a2));
  box-shadow:0 12px 40px rgba(109,107,255,.45); animation:float 6s ease-in-out infinite;}
.pill{display:inline-flex;align-items:center;gap:8px;font-size:13px;color:var(--muted);
  border:1px solid var(--line2);background:var(--card);padding:6px 14px;border-radius:999px;
  backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);margin-bottom:24px;}
.dot{width:8px;height:8px;border-radius:50%;background:var(--ok);animation:pulse 2s infinite;}
.hero h1{font-family:'Space Grotesk';font-weight:700;font-size:54px;line-height:1.05;
  letter-spacing:-1.5px;margin:0 0 14px;
  background:linear-gradient(180deg,#fff,#aeb6cc);-webkit-background-clip:text;background-clip:text;color:transparent;}
.rotator{height:34px;overflow:hidden;display:inline-block;vertical-align:bottom;}
.rotator .track{display:flex;flex-direction:column;animation:slide 9s cubic-bezier(.8,0,.2,1) infinite;}
.rotator span{height:34px;line-height:34px;font-family:'Space Grotesk';font-weight:600;font-size:25px;
  background:linear-gradient(90deg,var(--a3),var(--a1),var(--a2));-webkit-background-clip:text;background-clip:text;color:transparent;}
.subtitle{font-size:25px;color:var(--muted);font-weight:500;margin:2px 0 18px;}
.lede{max-width:620px;margin:0 auto 30px;color:var(--muted);font-size:16px;line-height:1.7;}
.ctas{display:flex;gap:12px;justify-content:center;flex-wrap:wrap;}
.btn{display:inline-flex;align-items:center;gap:8px;padding:11px 20px;border-radius:11px;
  font-weight:600;font-size:14px;text-decoration:none;transition:.25s;border:1px solid var(--line2);}
.btn.primary{background:linear-gradient(135deg,var(--a1),var(--a2));color:#fff;border:none;
  box-shadow:0 8px 24px rgba(109,107,255,.4);}
.btn.primary:hover{transform:translateY(-2px);box-shadow:0 12px 32px rgba(109,107,255,.55);}
.btn.ghost{background:var(--card);color:var(--txt);backdrop-filter:blur(10px);}
.btn.ghost:hover{border-color:var(--a1);color:#fff;transform:translateY(-2px);}

/* KPI band */
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:40px 0 8px;}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:22px 16px;text-align:center;
  backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);transition:.25s;animation:pop .6s ease backwards;}
.kpi:hover{transform:translateY(-4px);border-color:var(--line2);}
.kpi .n{font-family:'Space Grotesk';font-weight:700;font-size:38px;letter-spacing:-1px;
  background:linear-gradient(135deg,#fff,var(--a1));-webkit-background-clip:text;background-clip:text;color:transparent;}
.kpi .l{font-size:12.5px;color:var(--muted);margin-top:4px;letter-spacing:.3px;}

/* sections */
.sec{margin:64px 0 0;}
.eyebrow{font-size:12px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:var(--a1);margin-bottom:8px;}
.sec h2{font-family:'Space Grotesk';font-weight:700;font-size:30px;letter-spacing:-.5px;margin:0 0 6px;color:#fff;}
.sec .desc{color:var(--muted);font-size:15px;margin-bottom:26px;}

/* project case studies */
.proj{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:26px;margin-bottom:18px;
  backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);transition:.3s;position:relative;overflow:hidden;}
.proj::before{content:"";position:absolute;inset:0 0 auto 0;height:2px;
  background:linear-gradient(90deg,var(--a3),var(--a1),var(--a2));opacity:0;transition:.3s;}
.proj:hover{transform:translateY(-5px);border-color:var(--line2);box-shadow:0 22px 60px rgba(0,0,0,.45);}
.proj:hover::before{opacity:1;}
.proj .top{display:flex;justify-content:space-between;align-items:flex-start;gap:14px;flex-wrap:wrap;margin-bottom:6px;}
.proj h3{font-family:'Space Grotesk';font-weight:600;font-size:21px;margin:0;color:#fff;}
.proj .meta{font-size:12.5px;color:var(--faint);white-space:nowrap;}
.proj .live{font-size:12px;color:var(--a3);text-decoration:none;border:1px solid var(--line2);
  padding:4px 10px;border-radius:8px;transition:.2s;}
.proj .live:hover{border-color:var(--a3);background:rgba(34,211,238,.08);}
.pa{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin:16px 0 14px;}
.pa .b .k{font-size:11px;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:var(--faint);margin-bottom:5px;}
.pa .b .v{font-size:13.5px;color:var(--txt);line-height:1.55;}
.chips{display:flex;flex-wrap:wrap;gap:7px;}
.chip{font-size:11.5px;color:var(--muted);background:rgba(255,255,255,.05);border:1px solid var(--line);
  padding:4px 11px;border-radius:999px;transition:.2s;}
.proj:hover .chip{border-color:var(--line2);}

/* timeline */
.tl{position:relative;padding-left:26px;}
.tl::before{content:"";position:absolute;left:6px;top:6px;bottom:6px;width:2px;
  background:linear-gradient(180deg,var(--a1),var(--a2),transparent);}
.tl .it{position:relative;margin-bottom:22px;}
.tl .it::before{content:"";position:absolute;left:-26px;top:4px;width:12px;height:12px;border-radius:50%;
  background:var(--a1);box-shadow:0 0 0 4px rgba(109,107,255,.18);}
.tl .it .when{font-size:12px;color:var(--faint);}
.tl .it .role{font-family:'Space Grotesk';font-weight:600;font-size:16px;color:#fff;margin:2px 0;}
.tl .it .org{font-size:13.5px;color:var(--a1);margin-bottom:4px;}
.tl .it .d{font-size:13.5px;color:var(--muted);line-height:1.55;}

/* skills */
.sg{margin-bottom:16px;}
.sg .h{font-size:13px;font-weight:700;color:var(--muted);margin-bottom:9px;}
.sg .row{display:flex;flex-wrap:wrap;gap:8px;}
.sk{font-size:13px;color:var(--txt);background:var(--card);border:1px solid var(--line);
  padding:7px 14px;border-radius:10px;transition:.2s;backdrop-filter:blur(8px);}
.sk:hover{border-color:var(--a1);color:#fff;transform:translateY(-2px);}

/* chat */
.chat-head{text-align:center;margin:18px 0 6px;}
.chat-head .tag{font-size:12px;color:var(--a3);letter-spacing:1px;}
[data-testid="stChatMessage"]{background:var(--card)!important;border:1px solid var(--line);
  border-radius:14px!important;backdrop-filter:blur(10px);}
[data-testid="stChatInput"] textarea{background:var(--bg2)!important;}
.foot{text-align:center;margin:70px 0 10px;color:var(--faint);font-size:13px;}
.foot a{color:var(--muted);text-decoration:none;} .foot a:hover{color:var(--a1);}

@media(max-width:640px){
  .hero h1{font-size:38px;} .kpis{grid-template-columns:repeat(2,1fr);} .pa{grid-template-columns:1fr;}
  .subtitle,.rotator span{font-size:20px;}
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ----------------------------- HERO -----------------------------
st.markdown(f"""
<div class="hero reveal">
  <div class="avatar">PP</div>
  <div class="pill"><span class="dot"></span> Available immediately · Delhi NCR · Hybrid / Remote / On-site</div>
  <h1>Priyanshu Pandey</h1>
  <div class="subtitle">I build &amp; ship&nbsp;
    <span class="rotator"><span class="track">
      <span>LLM applications</span>
      <span>RAG systems</span>
      <span>AI agents</span>
      <span>NLP models</span>
      <span>LLM applications</span>
    </span></span>
  </div>
  <p class="lede">Applied AI engineer (B.Tech, AI &amp; ML · 8.3 CGPA) who turns large language models into
  real, deployed products — from this RAG portfolio you're reading to 10 persona-based GenAI apps in production.</p>
  <div class="ctas">
    <a class="btn primary" href="#ask">✦ Ask my AI anything</a>
    <a class="btn ghost" href="{GITHUB}" target="_blank">GitHub</a>
    <a class="btn ghost" href="{LINKEDIN}" target="_blank">LinkedIn</a>
    <a class="btn ghost" href="{RESUME_URL}" target="_blank">Résumé</a>
  </div>
</div>
""", unsafe_allow_html=True)

# ----------------------------- KPI BAND -----------------------------
st.markdown("""
<div class="kpis reveal">
  <div class="kpi" style="animation-delay:.05s"><div class="n">10</div><div class="l">GenAI apps shipped</div></div>
  <div class="kpi" style="animation-delay:.15s"><div class="n">3</div><div class="l">Engineering internships</div></div>
  <div class="kpi" style="animation-delay:.25s"><div class="n">4</div><div class="l">Projects deployed</div></div>
  <div class="kpi" style="animation-delay:.35s"><div class="n">8.3</div><div class="l">CGPA / 10</div></div>
</div>
""", unsafe_allow_html=True)

# ----------------------------- PROJECTS (CASE STUDIES) -----------------------------
def project(title, meta, problem, approach, impact, chips, live=None):
    live_html = f'<a class="live" href="{live}" target="_blank">↗ Live</a>' if live else ''
    chip_html = "".join(f'<span class="chip">{c}</span>' for c in chips)
    return f"""
    <div class="proj reveal">
      <div class="top">
        <div><h3>{title}</h3><div class="meta">{meta}</div></div>{live_html}
      </div>
      <div class="pa">
        <div class="b"><div class="k">Problem</div><div class="v">{problem}</div></div>
        <div class="b"><div class="k">Approach</div><div class="v">{approach}</div></div>
        <div class="b"><div class="k">Impact</div><div class="v">{impact}</div></div>
      </div>
      <div class="chips">{chip_html}</div>
    </div>"""

st.markdown('<div class="sec"><div class="eyebrow">Selected Work</div>'
            '<h2>Projects, as case studies</h2>'
            '<div class="desc">Not just what I built — the problem, the engineering decision, and the outcome.</div></div>',
            unsafe_allow_html=True)

st.markdown(project(
    "Ask Priyanshu's AI — this site",
    "Retrieval-Augmented Generation · 2026",
    "A static resume can't answer a recruiter's specific question, and LLMs hallucinate facts about people.",
    "Built a RAG pipeline: chunk → sentence-transformer embeddings → semantic retrieval → grounded LLM answer with a strict 'answer only from context' guardrail. Graceful TF-IDF fallback.",
    "A live, verifiable demo recruiters can interrogate — zero hallucination, sources shown. Deployed publicly.",
    ["Python","RAG","sentence-transformers","Vector Search","Groq LLM","Streamlit"],
    live="https://ask-priyanshu.streamlit.app") , unsafe_allow_html=True)

st.markdown(project(
    "10 Persona-Based Generative AI Applications",
    "USO India · AI Application Engineer · 2026",
    "One product had to serve 10 distinct user personas, each needing a different tone, flow, and AI behaviour.",
    "Designed a shared LLM backend with per-persona system prompts, context-management rules, and output guardrails; owned API integration and responsive web/mobile delivery.",
    "Shipped all 10 apps with consistent, on-persona output from a single reusable architecture.",
    ["LLM API Integration","Prompt Engineering","Context Management","Python","REST APIs"]) , unsafe_allow_html=True)

st.markdown(project(
    "Municipal AI Chatbot (NLP)",
    "NDMC · ML Intern · 2025",
    "Citizen queries needed automated handling, but there was zero labelled training data to start from.",
    "Defined the intent taxonomy, annotated the dataset by hand from raw logs, then fine-tuned a Transformer (Hugging Face) for intent detection + NER, iterating against real queries.",
    "Delivered a tested, working chatbot from zero labelled data within the internship window.",
    ["Transformer Fine-tuning","Hugging Face","Intent Detection","NER","Python"]) , unsafe_allow_html=True)

st.markdown(project(
    "Delhi Demand Prediction",
    "Academic · VIPS-TC · 2024",
    "Predict service/resource demand across Delhi zones from messy public data.",
    "Full EDA + feature engineering, then benchmarked Linear Regression, Random Forest, and XGBoost via cross-validation; visualised results in Power BI.",
    "A validated model comparison with a clear, communicable winner and decision rationale.",
    ["Machine Learning","XGBoost","Random Forest","Feature Engineering","Power BI"]) , unsafe_allow_html=True)

# ----------------------------- EXPERIENCE TIMELINE -----------------------------
st.markdown("""
<div class="sec"><div class="eyebrow">Trajectory</div>
<h2>Experience</h2>
<div class="desc">Three engineering internships across GenAI, NLP, and backend.</div>
<div class="tl">
  <div class="it reveal"><div class="when">Feb 2026 – Jun 2026</div>
    <div class="role">AI Application Engineer (Intern)</div><div class="org">USO India</div>
    <div class="d">Shipped 10 persona-based GenAI apps — LLM integration, prompt engineering, context management, deployment.</div></div>
  <div class="it reveal"><div class="when">Jul 2025 – Aug 2025</div>
    <div class="role">Machine Learning Intern (NLP)</div><div class="org">NDMC — Citizen Services</div>
    <div class="d">Built & fine-tuned an intent + NER chatbot from zero labelled data; owned the full data pipeline.</div></div>
  <div class="it reveal"><div class="when">Jul 2024 – Aug 2024</div>
    <div class="role">Software Development Intern</div><div class="org">NDMC — Inventory Management</div>
    <div class="d">Built RESTful APIs for asset tracking & automated order triggers; Python/SQL backend.</div></div>
  <div class="it reveal"><div class="when">2022 – 2026</div>
    <div class="role">B.Tech, Artificial Intelligence & Machine Learning</div><div class="org">VIPS-TC (GGSIPU), New Delhi</div>
    <div class="d">CGPA 8.3 / 10 · provisional degree July 2026.</div></div>
</div></div>
""", unsafe_allow_html=True)

# ----------------------------- SKILLS -----------------------------
def skillgroup(h, items):
    row = "".join(f'<span class="sk">{i}</span>' for i in items)
    return f'<div class="sg"><div class="h">{h}</div><div class="row">{row}</div></div>'

st.markdown('<div class="sec"><div class="eyebrow">Toolkit</div><h2>Technical skills</h2>'
            '<div class="desc">Weighted toward what I actually ship with.</div></div>', unsafe_allow_html=True)
st.markdown('<div class="reveal">' +
    skillgroup("Generative AI & LLM", ["LLM API Integration","Prompt Engineering","RAG","Context Management","AI Automation","Vector Databases"]) +
    skillgroup("NLP", ["Transformer Fine-tuning","Hugging Face","Intent Detection","NER","Text Classification"]) +
    skillgroup("Machine Learning", ["scikit-learn","TensorFlow","XGBoost","Random Forest","Feature Engineering","EDA"]) +
    skillgroup("Languages & Backend", ["Python","SQL","JavaScript","FastAPI","REST APIs","Git","Docker (basics)"]) +
    '</div>', unsafe_allow_html=True)

# ----------------------------- CHAT (RAG centerpiece) -----------------------------
st.markdown('<div class="sec" id="ask"><div class="eyebrow">Interactive</div>'
            '<h2>Ask my AI anything</h2>'
            '<div class="desc">A live RAG chatbot grounded in my real background — try “What did he build at NDMC?” '
            'or “Is he available immediately?”. Answers cite the facts they use.</div></div>',
            unsafe_allow_html=True)

@st.cache_resource
def setup():
    chunks = load_chunks()
    retrieve, mode = build_retriever(chunks)
    return chunks, retrieve, mode

chunks, retrieve, mode = setup()

if "history" not in st.session_state:
    st.session_state.history = []
for role, m in st.session_state.history:
    with st.chat_message(role, avatar="✦" if role == "assistant" else "🧑‍💻"):
        st.markdown(m)

q = st.chat_input("Ask about Priyanshu's skills, projects, or experience…")
if q:
    st.session_state.history.append(("user", q))
    with st.chat_message("user", avatar="🤖"):
        st.markdown(q)
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Retrieving facts…"):
            reply, used = answer_question(q, retrieve)
        st.markdown(reply)
        with st.expander("📚 Sources used"):
            for i, c in enumerate(used, 1):
                st.markdown(f"**{i}.** {c}")
    st.session_state.history.append(("assistant", reply))

# ----------------------------- FOOTER -----------------------------
st.markdown(f"""
<div class="foot">
  Built with Python &amp; a RAG pipeline · retrieval mode: <code>{mode}</code><br>
  <a href="mailto:{EMAIL}">{EMAIL}</a> &nbsp;·&nbsp; {PHONE} &nbsp;·&nbsp;
  <a href="{GITHUB}" target="_blank">GitHub</a> &nbsp;·&nbsp;
  <a href="{LINKEDIN}" target="_blank">LinkedIn</a>
</div>
""", unsafe_allow_html=True)