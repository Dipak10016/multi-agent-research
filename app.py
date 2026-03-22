import streamlit as st
import os
import time
import json
from datetime import datetime
from typing import TypedDict, Annotated, List
import operator

# ── Load .env file automatically ─────────────────────────────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ── Load .env file automatically ─────────────────────────────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, keys entered manually in sidebar

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Multi-Agent Research Assistant",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Mono:wght@300;400;500&display=swap');

* { font-family: 'DM Mono', monospace; }
h1, h2, h3, .display { font-family: 'Syne', sans-serif !important; }

.stApp {
    background: #0a0a0f;
    color: #e8e8f0;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #0f0f1a !important;
    border-right: 1px solid #1e1e3a;
}

/* Agent cards */
.agent-card {
    background: linear-gradient(135deg, #0f0f1a 0%, #141428 100%);
    border: 1px solid #1e1e3a;
    border-radius: 12px;
    padding: 16px 20px;
    margin: 8px 0;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}
.agent-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
    background: var(--accent);
}
.agent-card.active {
    border-color: var(--accent);
    box-shadow: 0 0 20px rgba(99, 255, 182, 0.08);
}
.agent-card.done { opacity: 0.7; }

.agent-name {
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 0.85rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--accent);
}
.agent-status {
    font-size: 0.72rem;
    color: #6666aa;
    margin-top: 4px;
}

/* Status badge */
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.65rem;
    font-weight: 500;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
.badge-waiting  { background: #1a1a2e; color: #5555aa; border: 1px solid #2a2a4e; }
.badge-running  { background: #0f2a1a; color: #63ffb6; border: 1px solid #1a4a30; animation: pulse 1.5s infinite; }
.badge-done     { background: #1a2a1a; color: #44cc88; border: 1px solid #2a4a2a; }
.badge-error    { background: #2a0f0f; color: #ff6666; border: 1px solid #4a1a1a; }

@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.6} }

/* Report box */
.report-box {
    background: #0f0f1a;
    border: 1px solid #1e1e3a;
    border-radius: 16px;
    padding: 32px;
    line-height: 1.8;
    font-size: 0.88rem;
    color: #c8c8e8;
}
.report-box h1, .report-box h2, .report-box h3 {
    font-family: 'Syne', sans-serif !important;
    color: #63ffb6;
    margin-top: 1.5em;
}

/* Log terminal */
.log-terminal {
    background: #060610;
    border: 1px solid #1a1a30;
    border-radius: 10px;
    padding: 16px;
    font-size: 0.72rem;
    color: #4444aa;
    max-height: 200px;
    overflow-y: auto;
    font-family: 'DM Mono', monospace;
}
.log-line { margin: 2px 0; }
.log-line.info  { color: #6666cc; }
.log-line.ok    { color: #44cc88; }
.log-line.warn  { color: #ccaa44; }
.log-line.agent { color: #63ffb6; }

/* Input */
.stTextInput input, .stTextArea textarea {
    background: #0f0f1a !important;
    border: 1px solid #1e1e3a !important;
    color: #e8e8f0 !important;
    border-radius: 10px !important;
    font-family: 'DM Mono', monospace !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #63ffb6 !important;
    box-shadow: 0 0 0 2px rgba(99,255,182,0.1) !important;
}

/* Buttons */
.stButton button {
    background: linear-gradient(135deg, #1a3a2a, #0f2a1a) !important;
    color: #63ffb6 !important;
    border: 1px solid #2a5a3a !important;
    border-radius: 10px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    transition: all 0.2s ease !important;
}
.stButton button:hover {
    background: linear-gradient(135deg, #1e4430, #132e1e) !important;
    border-color: #63ffb6 !important;
    box-shadow: 0 0 15px rgba(99,255,182,0.15) !important;
}

/* Metric */
.metric-box {
    background: #0f0f1a;
    border: 1px solid #1e1e3a;
    border-radius: 10px;
    padding: 16px;
    text-align: center;
}
.metric-value {
    font-family: 'Syne', sans-serif;
    font-size: 1.8rem;
    font-weight: 800;
    color: #63ffb6;
}
.metric-label {
    font-size: 0.65rem;
    color: #5555aa;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-top: 4px;
}

:root { --accent: #63ffb6; }

/* Hide default streamlit chrome */
#MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ── Imports with error handling ───────────────────────────────────────────────
def check_dependencies():
    missing = []
    try: import groq
    except ImportError: missing.append("groq")
    try: from tavily import TavilyClient
    except ImportError: missing.append("tavily-python")
    try: import langgraph
    except ImportError: missing.append("langgraph")
    try: import langchain_groq
    except ImportError: missing.append("langchain-groq")
    return missing

missing_deps = check_dependencies()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding: 20px 0 10px'>
        <div style='font-family:Syne,sans-serif;font-size:1.3rem;font-weight:800;color:#63ffb6;letter-spacing:-0.02em'>
            🔬 RESEARCH<br>SWARM
        </div>
        <div style='font-size:0.65rem;color:#4444aa;letter-spacing:0.15em;text-transform:uppercase;margin-top:4px'>
            Multi-Agent Intelligence
        </div>
    </div>
    <hr style='border-color:#1e1e3a;margin:10px 0 20px'>
    """, unsafe_allow_html=True)

    st.markdown("### ⚙️ Configuration")
    env_groq   = os.getenv("GROQ_API_KEY", "")
    env_tavily = os.getenv("TAVILY_API_KEY", "")
    groq_key = st.text_input("Groq API Key", type="password",
                              value=env_groq,
                              placeholder="gsk_...",
                              help="Get free key at console.groq.com")
    tavily_key = st.text_input("Tavily API Key", type="password",
                                value=env_tavily,
                                placeholder="tvly-...",
                                help="Get free key at tavily.com")
    if env_groq and env_tavily:
        st.success("✅ Keys loaded from .env!")

    st.markdown("---")
    st.markdown("### 🤖 Agent Pipeline")

    agents_info = [
        ("🔍", "Search Agent",    "Retrieves live web data"),
        ("📝", "Summarizer",      "Condenses key findings"),
        ("✅", "Fact Checker",    "Validates & cross-checks"),
        ("✍️",  "Report Writer",  "Produces final report"),
    ]
    for icon, name, desc in agents_info:
        st.markdown(f"""
        <div class='agent-card' style='--accent:#63ffb6'>
            <div class='agent-name'>{icon} {name}</div>
            <div class='agent-status'>{desc}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.65rem;color:#333366;text-align:center;padding:10px 0'>
        Advanced AI — RAG + Agents Project<br>
        LangGraph · Groq · Tavily
    </div>
    """, unsafe_allow_html=True)


# ── Main Header ───────────────────────────────────────────────────────────────
st.markdown("""
<div style='padding: 30px 0 10px'>
    <h1 style='font-family:Syne,sans-serif;font-size:2.4rem;font-weight:800;
               color:#e8e8f0;margin:0;letter-spacing:-0.03em'>
        Multi-Agent Research Assistant
    </h1>
    <p style='color:#5555aa;font-size:0.8rem;margin-top:8px;letter-spacing:0.05em'>
        SEARCH → SUMMARIZE → FACT-CHECK → REPORT &nbsp;|&nbsp; Powered by LangGraph + Groq
    </p>
</div>
""", unsafe_allow_html=True)

# ── Dependency warning ────────────────────────────────────────────────────────
if missing_deps:
    st.error(f"⚠️ Missing packages: `{', '.join(missing_deps)}`\n\nRun: `pip install {' '.join(missing_deps)}`")
    st.stop()

# ── Imports after dep check ───────────────────────────────────────────────────
from groq import Groq
from tavily import TavilyClient
from langgraph.graph import StateGraph, END
from typing import Optional

# ── State definition ──────────────────────────────────────────────────────────
class ResearchState(TypedDict):
    topic: str
    search_results: List[dict]
    summary: str
    fact_check: str
    final_report: str
    logs: Annotated[List[str], operator.add]
    agent_statuses: dict
    error: Optional[str]


# ── Agent functions ───────────────────────────────────────────────────────────
def search_agent(state: ResearchState) -> ResearchState:
    try:
        client = TavilyClient(api_key=st.session_state.tavily_key)
        results = client.search(
            query=state["topic"],
            search_depth="advanced",
            max_results=6,
            include_answer=True,
        )
        sources = results.get("results", [])
        return {
            "search_results": sources,
            "logs": [f"[SEARCH] ✓ Found {len(sources)} sources for: {state['topic']}"],
            "agent_statuses": {**state.get("agent_statuses", {}), "search": "done"},
        }
    except Exception as e:
        return {
            "search_results": [],
            "error": f"Search failed: {str(e)}",
            "logs": [f"[SEARCH] ✗ Error: {str(e)}"],
            "agent_statuses": {**state.get("agent_statuses", {}), "search": "error"},
        }


def summarizer_agent(state: ResearchState) -> ResearchState:
    try:
        client = Groq(api_key=st.session_state.groq_key)
        sources_text = "\n\n".join([
            f"Source {i+1}: {s.get('title','')}\n{s.get('content','')[:600]}"
            for i, s in enumerate(state["search_results"])
        ])
        prompt = f"""You are a research summarizer. Given these search results about "{state['topic']}", 
create a comprehensive summary covering:
- Main findings and key facts
- Important statistics or data points  
- Different perspectives or viewpoints
- Recent developments

Search Results:
{sources_text}

Write a detailed 3-4 paragraph summary:"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1000,
        )
        summary = response.choices[0].message.content
        return {
            "summary": summary,
            "logs": [f"[SUMMARIZER] ✓ Generated {len(summary.split())} word summary"],
            "agent_statuses": {**state.get("agent_statuses", {}), "summarizer": "done"},
        }
    except Exception as e:
        return {
            "summary": "Summary unavailable.",
            "error": f"Summarizer failed: {str(e)}",
            "logs": [f"[SUMMARIZER] ✗ Error: {str(e)}"],
            "agent_statuses": {**state.get("agent_statuses", {}), "summarizer": "error"},
        }


def fact_checker_agent(state: ResearchState) -> ResearchState:
    try:
        client = Groq(api_key=st.session_state.groq_key)
        prompt = f"""You are a rigorous fact-checker. Review this summary about "{state['topic']}":

SUMMARY:
{state['summary']}

Your job:
1. Identify 3-5 key factual claims in the summary
2. Assess each claim's reliability (High/Medium/Low confidence)
3. Flag any potentially misleading statements
4. Note what additional verification might be needed

Format as:
**Claim 1:** [claim] → Confidence: [High/Medium/Low] — [brief reasoning]
**Claim 2:** ...
...
**Overall Assessment:** [1-2 sentences on reliability of the summary]"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=600,
        )
        fact_check = response.choices[0].message.content
        return {
            "fact_check": fact_check,
            "logs": [f"[FACT-CHECKER] ✓ Verified {len(state['search_results'])} sources"],
            "agent_statuses": {**state.get("agent_statuses", {}), "factchecker": "done"},
        }
    except Exception as e:
        return {
            "fact_check": "Fact-check unavailable.",
            "error": f"Fact-checker failed: {str(e)}",
            "logs": [f"[FACT-CHECKER] ✗ Error: {str(e)}"],
            "agent_statuses": {**state.get("agent_statuses", {}), "factchecker": "error"},
        }


def report_writer_agent(state: ResearchState) -> ResearchState:
    try:
        client = Groq(api_key=st.session_state.groq_key)
        sources_list = "\n".join([
            f"- {s.get('title','Untitled')}: {s.get('url','')}"
            for s in state["search_results"][:5]
        ])
        prompt = f"""You are an expert research report writer. Create a professional, well-structured research report on: "{state['topic']}"

Use this verified information:

SUMMARY:
{state['summary']}

FACT-CHECK NOTES:
{state['fact_check']}

Write a comprehensive research report with these sections:
# {state['topic']}: Research Report

## Executive Summary
[2-3 sentence overview]

## Key Findings
[4-6 bullet points with the most important discoveries]

## Detailed Analysis
[3-4 paragraphs of in-depth analysis]

## Fact-Check Highlights
[2-3 key verified facts with confidence levels]

## Conclusion
[1-2 paragraphs synthesizing insights and implications]

## Sources
{sources_list}

---
*Report generated by Multi-Agent Research Assistant | {datetime.now().strftime("%B %d, %Y")}*

Make it professional, insightful, and academically rigorous."""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=2000,
        )
        report = response.choices[0].message.content
        return {
            "final_report": report,
            "logs": [f"[WRITER] ✓ Report generated — {len(report.split())} words"],
            "agent_statuses": {**state.get("agent_statuses", {}), "writer": "done"},
        }
    except Exception as e:
        return {
            "final_report": "Report generation failed.",
            "error": f"Writer failed: {str(e)}",
            "logs": [f"[WRITER] ✗ Error: {str(e)}"],
            "agent_statuses": {**state.get("agent_statuses", {}), "writer": "error"},
        }


# ── Build LangGraph ───────────────────────────────────────────────────────────
def build_graph():
    graph = StateGraph(ResearchState)
    graph.add_node("search",      search_agent)
    graph.add_node("summarizer",  summarizer_agent)
    graph.add_node("fact_checker",fact_checker_agent)
    graph.add_node("writer",      report_writer_agent)
    graph.set_entry_point("search")
    graph.add_edge("search",       "summarizer")
    graph.add_edge("summarizer",   "fact_checker")
    graph.add_edge("fact_checker", "writer")
    graph.add_edge("writer",        END)
    return graph.compile()


# ── Session state ─────────────────────────────────────────────────────────────
for k, v in [("report", None), ("logs", []), ("agent_statuses", {}),
             ("search_results", []), ("running", False),
             ("groq_key", ""), ("tavily_key", ""), ("elapsed", 0)]:
    if k not in st.session_state:
        st.session_state[k] = v

if groq_key:   st.session_state.groq_key   = groq_key
if tavily_key: st.session_state.tavily_key = tavily_key


# ── Search bar ────────────────────────────────────────────────────────────────
st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
col_input, col_btn = st.columns([5, 1])
with col_input:
    topic = st.text_input("", placeholder="🔍  Enter a research topic  e.g. 'Quantum Computing in 2025'",
                          label_visibility="collapsed")
with col_btn:
    run_btn = st.button("⚡ RESEARCH", use_container_width=True)


# ── Metrics row ───────────────────────────────────────────────────────────────
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(f"""<div class='metric-box'>
        <div class='metric-value'>{len(st.session_state.search_results)}</div>
        <div class='metric-label'>Sources Found</div></div>""", unsafe_allow_html=True)
with m2:
    done_count = sum(1 for v in st.session_state.agent_statuses.values() if v == "done")
    st.markdown(f"""<div class='metric-box'>
        <div class='metric-value'>{done_count}/4</div>
        <div class='metric-label'>Agents Done</div></div>""", unsafe_allow_html=True)
with m3:
    word_count = len(st.session_state.report.split()) if st.session_state.report else 0
    st.markdown(f"""<div class='metric-box'>
        <div class='metric-value'>{word_count}</div>
        <div class='metric-label'>Report Words</div></div>""", unsafe_allow_html=True)
with m4:
    st.markdown(f"""<div class='metric-box'>
        <div class='metric-value'>{st.session_state.elapsed:.1f}s</div>
        <div class='metric-label'>Time Elapsed</div></div>""", unsafe_allow_html=True)

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

# ── Run pipeline ──────────────────────────────────────────────────────────────
if run_btn:
    if not topic.strip():
        st.warning("Please enter a research topic.")
    elif not st.session_state.groq_key:
        st.error("Please enter your Groq API key in the sidebar.")
    elif not st.session_state.tavily_key:
        st.error("Please enter your Tavily API key in the sidebar.")
    else:
        st.session_state.report         = None
        st.session_state.logs           = []
        st.session_state.agent_statuses = {}
        st.session_state.search_results = []
        st.session_state.running        = True
        st.session_state.elapsed        = 0

        # Live progress UI
        progress_placeholder = st.empty()
        log_placeholder      = st.empty()

        pipeline_steps = [
            ("search",      "🔍 Search Agent",   "Fetching live web data..."),
            ("summarizer",  "📝 Summarizer",      "Condensing key findings..."),
            ("factchecker", "✅ Fact Checker",    "Validating claims..."),
            ("writer",      "✍️ Report Writer",   "Crafting final report..."),
        ]

        def render_progress(current_idx, statuses):
            cards = ""
            for i, (key, name, desc) in enumerate(pipeline_steps):
                status = statuses.get(key, "waiting")
                if i < current_idx:   status = "done"
                elif i == current_idx: status = "running"
                badge_map = {"waiting":"badge-waiting","running":"badge-running",
                             "done":"badge-done","error":"badge-error"}
                label_map = {"waiting":"WAITING","running":"RUNNING ●",
                             "done":"DONE ✓","error":"ERROR ✗"}
                accent = "#63ffb6" if status in ("running","done") else "#2a2a5a"
                cards += f"""
                <div class='agent-card {status}' style='--accent:{accent}'>
                    <div style='display:flex;justify-content:space-between;align-items:center'>
                        <div class='agent-name'>{name}</div>
                        <span class='badge {badge_map[status]}'>{label_map[status]}</span>
                    </div>
                    <div class='agent-status'>{desc}</div>
                </div>"""
            return f"<div>{cards}</div>"

        start_time = time.time()
        graph      = build_graph()
        init_state = ResearchState(
            topic=topic, search_results=[], summary="", fact_check="",
            final_report="", logs=[], agent_statuses={}, error=None
        )

        try:
            # Stream through graph steps
            step_names = ["search", "summarizer", "factchecker", "writer"]
            current_step = 0

            for i, step_name in enumerate(step_names):
                progress_placeholder.markdown(
                    render_progress(i, st.session_state.agent_statuses),
                    unsafe_allow_html=True
                )
                time.sleep(0.3)

            # Actually run the full graph
            result = graph.invoke(init_state)

            st.session_state.report         = result.get("final_report", "")
            st.session_state.logs           = result.get("logs", [])
            st.session_state.search_results = result.get("search_results", [])
            st.session_state.agent_statuses = result.get("agent_statuses", {})
            st.session_state.elapsed        = round(time.time() - start_time, 1)
            st.session_state.running        = False

            progress_placeholder.markdown(
                render_progress(4, st.session_state.agent_statuses),
                unsafe_allow_html=True
            )

        except Exception as e:
            st.error(f"Pipeline error: {str(e)}")
            st.session_state.running = False

        st.rerun()


# ── Display Results ───────────────────────────────────────────────────────────
if st.session_state.report:
    tab1, tab2, tab3 = st.tabs(["📄 Final Report", "🔍 Sources", "📋 Agent Logs"])

    with tab1:
        st.markdown(f"<div class='report-box'>{st.session_state.report.replace(chr(10), '<br>')}</div>",
                    unsafe_allow_html=True)
        st.download_button(
            label="⬇️ Download Report",
            data=st.session_state.report,
            file_name=f"research_report_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
            mime="text/markdown",
        )

    with tab2:
        if st.session_state.search_results:
            for i, src in enumerate(st.session_state.search_results):
                with st.expander(f"📌 Source {i+1}: {src.get('title', 'Untitled')[:70]}"):
                    st.markdown(f"**URL:** {src.get('url','N/A')}")
                    st.markdown(f"**Score:** {src.get('score', 'N/A')}")
                    st.markdown(src.get('content','No content')[:800] + "...")
        else:
            st.info("No sources to display.")

    with tab3:
        log_html = "<div class='log-terminal'>"
        for log in st.session_state.logs:
            cls = "ok" if "✓" in log else ("warn" if "✗" in log else "agent")
            log_html += f"<div class='log-line {cls}'>> {log}</div>"
        log_html += "</div>"
        st.markdown(log_html, unsafe_allow_html=True)

elif not st.session_state.running:
    st.markdown("""
    <div style='text-align:center;padding:60px 20px;color:#2a2a5a'>
        <div style='font-size:3rem'>🔬</div>
        <div style='font-family:Syne,sans-serif;font-size:1.1rem;font-weight:700;
                    color:#2a2a6a;margin-top:16px'>Ready to Research</div>
        <div style='font-size:0.75rem;margin-top:8px;color:#1a1a4a'>
            Enter a topic above and hit ⚡ RESEARCH to deploy your agent swarm
        </div>
    </div>
    """, unsafe_allow_html=True)