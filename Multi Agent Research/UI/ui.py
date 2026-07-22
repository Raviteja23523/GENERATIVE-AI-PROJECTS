import os
import sys

import streamlit as st

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REASEACH_DIR = os.path.join(PROJECT_ROOT, "REASEACH")

for path in (PROJECT_ROOT, REASEACH_DIR):
    if path not in sys.path:
        sys.path.append(path)

from REASEACH.pipeline import run_research_pipeline

# ==========================================
# Page Configuration
# ==========================================
st.set_page_config(
    page_title="ResearchMind",
    page_icon="🚀",
    layout="centered"
)

# ==========================================
# Custom CSS
# ==========================================
st.markdown("""
<style>

.stApp{
    background:#09090f;
    color:white;
}

.block-container{
    max-width:820px;
    padding-top:3rem;
    padding-bottom:2rem;
}

.title{
    text-align:center;
    font-size:64px;
    font-weight:900;
    letter-spacing:-2px;
    margin-bottom:0;
    line-height:1.1;
}

.orange{
    color:#ff7b1c;
}

.subtitle{
    text-align:center;
    color:#9ca3af;
    margin-bottom:32px;
    font-size:16px;
}

/* Input styling */
div[data-testid="stTextInput"] input{
    background:rgba(255,255,255,0.04);
    border:1px solid rgba(255,255,255,0.08);
    border-radius:12px;
    color:white;
    padding:14px 16px;
    font-size:15px;
}

div[data-testid="stTextInput"] label{
    color:#e5e7eb;
    font-weight:600;
    font-size:14px;
}

/* Run button */
div.stButton > button{
    width:100%;
    height:50px;
    background:#ff7b1c;
    color:white;
    border:none;
    border-radius:12px;
    font-weight:bold;
    font-size:16px;
    margin-top:10px;
}

div.stButton > button:hover{
    background:#ff8d3d;
}

/* Pipeline step chips - single row, equal height, no stretch issues */
.pipeline-row{
    display:flex;
    gap:10px;
    margin:20px 0 6px 0;
}

.chip{
    flex:1;
    background:#14141c;
    border:1px solid #222230;
    border-radius:12px;
    padding:12px 10px;
    text-align:center;
}

.chip-icon{
    font-size:20px;
    margin-bottom:4px;
}

.chip-label{
    font-size:12px;
    font-weight:600;
    color:#d4d4d8;
}

/* Native Streamlit status widget - restyle to match theme */
div[data-testid="stStatusWidget"]{
    background:#14141c;
    border:1px solid #222230;
    border-radius:12px;
}

/* Trim default per-element margins so nothing leaves dead space */
div[data-testid="stElementContainer"]{
    margin-bottom:0.4rem !important;
}

div[data-testid="stAlert"]{
    margin:0.3rem 0 !important;
}

hr{
    border-color:#222230 !important;
}

</style>
""", unsafe_allow_html=True)

# ==========================================
# Session State
# ==========================================
if "result" not in st.session_state:
    st.session_state.result = None
if "topic" not in st.session_state:
    st.session_state.topic = ""

# ==========================================
# Header
# ==========================================
st.markdown(
    '<div class="title">Research<span class="orange">Mind</span></div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="subtitle">Multi-Agent AI Research Pipeline</div>',
    unsafe_allow_html=True
)

# ==========================================
# Input + Run button (single column, no stretch issues)
# ==========================================
topic = st.text_input(
    "Research Topic",
    placeholder="Quantum Computing Breakthroughs in 2025"
)

run_btn = st.button("🚀 Run Research Pipeline")

# ==========================================
# Pipeline steps - single flex row, always equal height
# ==========================================
st.markdown("""
<div class="pipeline-row">
    <div class="chip">
        <div class="chip-icon">🔎</div>
        <div class="chip-label">Search Agent</div>
    </div>
    <div class="chip">
        <div class="chip-icon">📚</div>
        <div class="chip-label">Reader Agent</div>
    </div>
    <div class="chip">
        <div class="chip-icon">✍</div>
        <div class="chip-label">Writer Chain</div>
    </div>
    <div class="chip">
        <div class="chip-icon">📝</div>
        <div class="chip-label">Critic Chain</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# Run Pipeline (native st.status - no leftover placeholder space)
# ==========================================
if run_btn:

    if not topic.strip():
        st.warning("Please enter a research topic.")
        st.stop()

    with st.status("Running research pipeline...", expanded=True) as status:

        st.write("🔎 Search Agent running...")
        st.write("📚 Reader Agent running...")
        st.write("✍ Writer Chain generating report...")

        result = run_research_pipeline(topic)

        st.write("📝 Critic Chain evaluating report...")

        status.update(
            label="✅ Pipeline completed",
            state="complete",
            expanded=False
        )

    st.session_state.result = result
    st.session_state.topic = topic
    st.balloons()

# ==========================================
# Display Results
# ==========================================
if st.session_state.result is not None:

    result = st.session_state.result

    st.markdown("---")

    tab1, tab2, tab3, tab4 = st.tabs([
        "📄 Report",
        "🔎 Search Results",
        "📚 Scraped Content",
        "📝 Critic Feedback"
    ])

    with tab1:

        with st.container(border=True):
            st.markdown(result.get("report", "No report generated."))

        safe_name = st.session_state.topic.replace(" ", "_").replace("/", "_")

        st.download_button(
            "⬇ Download Report",
            data=result.get("report", ""),
            file_name=f"{safe_name}.md",
            mime="text/markdown"
        )

    with tab2:

        search_results = result.get("search_results", [])

        if isinstance(search_results, list):
            for item in search_results:
                st.markdown(f"- {item}")
        else:
            st.write(search_results)

    with tab3:

        scraped = result.get("scraped_content", {})

        if isinstance(scraped, dict):
            for url, content in scraped.items():
                with st.expander(url):
                    st.write(content)
        else:
            st.write(scraped)

    with tab4:

        st.info(result.get("feedback", "No feedback available."))

# ==========================================
# Footer
# ==========================================
st.markdown("---")
st.caption("🚀 Powered by Streamlit • AI Research Pipeline")