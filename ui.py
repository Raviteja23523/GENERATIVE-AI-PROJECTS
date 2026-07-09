import streamlit as st
from pipeline import run_research_pipeline
import time

st.set_page_config(
page_title="ResearchMind",
page_icon="🚀",
layout="wide"
)

# ==========================

# CSS

# ==========================

st.markdown("""

<style>

.stApp{
    background:#09090f;
    color:white;
}

.block-container{
    max-width:1200px;
    padding-top:2rem;
}

.title{
    text-align:center;
    font-size:72px;
    font-weight:900;
    letter-spacing:-2px;
}

.orange{
    color:#ff7b1c;
}

.subtitle{
    text-align:center;
    color:#9ca3af;
    margin-bottom:50px;
}

.glass{
    background:rgba(255,255,255,0.04);
    backdrop-filter:blur(12px);
    border:1px solid rgba(255,255,255,0.08);
    border-radius:18px;
    padding:20px;
}

.pipeline-card{
    background:#14141c;
    border:1px solid #222230;
    border-radius:15px;
    padding:18px;
    margin-bottom:12px;
}

.agent-title{
    font-size:18px;
    font-weight:700;
}

.agent-sub{
    font-size:13px;
    color:#a1a1aa;
}

div.stButton > button{
    background:#ff7b1c;
    color:white;
    width:100%;
    height:50px;
    border:none;
    border-radius:12px;
    font-weight:bold;
}

div.stButton > button:hover{
    background:#ff8d3d;
}

</style>

""", unsafe_allow_html=True)

# ==========================

# Header

# ==========================

st.markdown(
'<div class="title">Research<span class="orange">Mind</span></div>',
unsafe_allow_html=True
)

st.markdown(
'<div class="subtitle">Multi-Agent AI Research Pipeline</div>',
unsafe_allow_html=True
)

# ==========================

# Layout

# ==========================

left,right = st.columns([1.5,1])

with left:


    st.markdown('<div class="glass">', unsafe_allow_html=True)

    topic = st.text_input(
        "Research Topic",
        placeholder="Quantum Computing Breakthroughs in 2025"
    )

    run_btn = st.button("🚀 Run Research Pipeline")

    st.markdown('</div>', unsafe_allow_html=True)


    with right:


        st.markdown("### Pipeline")

        st.markdown("""
        <div class="pipeline-card">
            <div class="agent-title">🔎 Search Agent</div>
            <div class="agent-sub">Collect latest information</div>
        </div>

        <div class="pipeline-card">
            <div class="agent-title">📚 Reader Agent</div>
            <div class="agent-sub">Scrape and analyze content</div>
        </div>

        <div class="pipeline-card">
            <div class="agent-title">✍️ Writer Chain</div>
            <div class="agent-sub">Generate research report</div>
        </div>

        <div class="pipeline-card">
            <div class="agent-title">📝 Critic Chain</div>
            <div class="agent-sub">Review report quality</div>
        </div>
        """, unsafe_allow_html=True)


        # ==========================

        # Run Pipeline

        # ==========================

        if run_btn:

            if not topic:
                st.warning("Enter a topic")
                st.stop()

            st.markdown("---")

            status_box = st.empty()
            progress = st.progress(0)

            status_box.info("🔎 Search Agent Running...")
            progress.progress(20)

            time.sleep(0.5)

            status_box.info("📚 Reader Agent Running...")
            progress.progress(40)

            time.sleep(0.5)

            status_box.info("✍️ Writer Chain Running...")
            progress.progress(70)

            result = run_research_pipeline(topic)

            status_box.info("📝 Critic Chain Running...")
            progress.progress(90)

            time.sleep(0.5)

            progress.progress(100)
            status_box.success("✅ Pipeline Completed")

            st.balloons()

            st.markdown("---")

            tab1,tab2,tab3,tab4 = st.tabs(
                [
                    "📄 Report",
                    "🔎 Search Results",
                    "📚 Scraped Content",
                    "📝 Critic Feedback"
                ]
            )

            with tab1:
                st.markdown(result["report"])

                st.download_button(
                    "⬇ Download Report",
                    result["report"],
                    file_name=f"{topic}.md"
                )

            with tab2:
                st.write(result["search_results"])

            with tab3:
                st.write(result["scaraped_content"])

            with tab4:
                st.write(result["feedback"])

