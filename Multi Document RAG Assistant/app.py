"""Streamlit interface for the document RAG assistant."""

from pathlib import Path

import streamlit as st

from original import (
    ingest_documents,
    ask_question,
    remove_documents,
)

UPLOAD_FOLDER = Path("uploads")
SUPPORTED_TYPES = ["pdf", "docx", "txt", "csv"]


st.set_page_config(
    page_title="Document Intelligence",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        .stApp { background: #212121; }
        .block-container { max-width: 1180px; padding-top: 2.5rem; padding-bottom: 2rem; }
        [data-testid="stSidebar"] { background: #171717; border-right: 1px solid #303030; }
        [data-testid="stSidebar"] * { color: #E5E7EB; }
        [data-testid="stSidebar"] .stCaption { color: #98A2B3 !important; }
        .eyebrow { color: #10A37F; font-size: .78rem; font-weight: 700;
                   letter-spacing: .12em; text-transform: uppercase; margin-bottom: .4rem; }
        .hero-title { font-size: 2.45rem; font-weight: 750; letter-spacing: -0.04em;
                      margin: 0; color: #F8FAFC; }
        .hero-copy { color: #B4B4B4; font-size: 1.05rem; margin-top: .45rem; }
        .info-card { background: #2A2A2A; border: 1px solid #3A3A3A; border-radius: 14px;
                     padding: 1rem 1.1rem; min-height: 106px; }
        .info-card h4 { margin: 0 0 .35rem; color: #F8FAFC; font-size: .92rem; }
        .info-card p { margin: 0; color: #B4B4B4; font-size: .85rem; line-height: 1.45; }
        .chat-label { font-size: .8rem; color: #10A37F; font-weight: 650;
                      letter-spacing: .08em; text-transform: uppercase; margin: 1.8rem 0 .4rem; }
        .stButton > button { border-radius: 8px; font-weight: 650; border: 1px solid #4A4A4A; }
        .stButton > button[kind="primary"] { background: #10A37F; color: white; border-color: #10A37F; }
        .stButton > button[kind="primary"]:hover { background: #0D8B6B; border-color: #0D8B6B; }
        .stButton > button[kind="secondary"] { background: #2F2F2F; color: #ECECEC; }
        [data-testid="stChatMessage"] { background: #2A2A2A; border: 1px solid #3A3A3A;
                                          border-radius: 14px; margin-bottom: .65rem; }
        [data-testid="stChatInput"] { border-radius: 12px; border: 1px solid #565656; background: #2F2F2F; }
        [data-testid="stChatInput"] textarea { color: #F8FAFC !important; }
        [data-testid="stFileUploader"] { border: 1px dashed #5A5A5A; border-radius: 10px; padding: .2rem; }
        [data-testid="stAlert"] { border-radius: 10px; }
        hr { border-color: #303030 !important; }
    </style>
    """,
    unsafe_allow_html=True,
)


def initialise_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "indexed_files" not in st.session_state:
        st.session_state.indexed_files = []


def save_uploaded_files(uploaded_files):
    """Save uploaded files locally and return their paths."""
    UPLOAD_FOLDER.mkdir(exist_ok=True)
    file_paths = []
    for uploaded_file in uploaded_files:
        save_path = UPLOAD_FOLDER / Path(uploaded_file.name).name
        save_path.write_bytes(uploaded_file.getbuffer())
        file_paths.append(str(save_path))
    return file_paths


def get_uploaded_filenames():
    """Return supported files that are already available in the uploads folder."""
    if not UPLOAD_FOLDER.exists():
        return []
    return sorted(
        file.name
        for file in UPLOAD_FOLDER.iterdir()
        if file.is_file() and file.suffix.lower().lstrip(".") in SUPPORTED_TYPES
    )


initialise_state()

with st.sidebar:
    st.markdown("## 📚 Document Intelligence")
    st.caption("Upload sources, then ask grounded questions.")
    st.divider()

    st.markdown("#### 1. Add sources")
    uploaded_files = st.file_uploader(
        "Upload documents",
        type=SUPPORTED_TYPES,
        accept_multiple_files=True,
        label_visibility="collapsed",
        help="Supported formats: PDF, DOCX, TXT, and CSV.",
    )
    st.caption("Supported: PDF, DOCX, TXT, CSV")

    if st.button("Index documents", type="primary", use_container_width=True):
        if not uploaded_files:
            st.warning("Upload at least one document first.")
        else:
            try:
                with st.status("Indexing documents...", expanded=True) as status:
                    st.write("Saving uploaded files")
                    file_paths = save_uploaded_files(uploaded_files)
                    st.write("Creating searchable document chunks")
                    ingest_documents(file_paths)
                    status.update(label="Documents indexed", state="complete", expanded=False)

                st.session_state.indexed_files = [file.name for file in uploaded_files]
                st.success(f"Indexed {len(uploaded_files)} document(s).")
            except Exception as error:
                st.error(f"Could not index the documents: {error}")

    if st.session_state.indexed_files:
        st.divider()
        st.markdown("#### Indexed this session")
        for file_name in st.session_state.indexed_files:
            st.caption(f"✓ {file_name}")

    st.divider()
    st.markdown("#### Manage documents")
    files_to_remove = st.multiselect(
        "Remove documents",
        options=get_uploaded_filenames(),
        placeholder="Select documents to remove",
        key="files_to_remove",
    )
    if st.button("Remove selected documents", use_container_width=True):
        if not files_to_remove:
            st.warning("Select at least one document to remove.")
        else:
            try:
                with st.spinner("Removing documents from the knowledge base..."):
                    removed_chunks = remove_documents(files_to_remove)
                    for file_name in files_to_remove:
                        file_path = UPLOAD_FOLDER / file_name
                        if file_path.exists():
                            file_path.unlink()

                st.session_state.indexed_files = [
                    file_name
                    for file_name in st.session_state.indexed_files
                    if file_name not in files_to_remove
                ]
                st.success(
                    f"Removed {len(files_to_remove)} file(s) and {removed_chunks} indexed chunk(s)."
                )
                st.rerun()
            except Exception as error:
                st.error(f"Could not remove the selected documents: {error}")

    st.divider()
    st.markdown("#### 2. Choose search scope")
    available_files = get_uploaded_filenames()
    search_scope = st.radio(
        "Search in",
        options=["All indexed documents", "Choose documents"],
        label_visibility="collapsed",
    )
    selected_files = None
    if search_scope == "Choose documents":
        file_query = st.text_input("Find a document", placeholder="Type a file name...")
        matching_files = [
            name for name in available_files if file_query.lower() in name.lower()
        ]
        selected_files = st.multiselect(
            "Documents to search",
            options=matching_files,
            placeholder="Select one or more documents",
        )
        if not available_files:
            st.caption("No supported files found in the uploads folder.")
        elif not matching_files:
            st.caption("No documents match that name.")
        elif not selected_files:
            st.caption("Select at least one document to narrow the search.")
    else:
        st.caption("Answers will use every indexed document.")

    st.divider()
    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


st.markdown('<p class="eyebrow">Document assistant</p>', unsafe_allow_html=True)
st.markdown('<h1 class="hero-title">Ask your documents,<br>with confidence.</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="hero-copy">Search the documents you index and receive answers grounded in their content.</p>',
    unsafe_allow_html=True,
)

first, second, third = st.columns(3)
with first:
    st.markdown('<div class="info-card"><h4>1. Upload</h4><p>Add PDFs, Word documents, text files, or CSVs in the sidebar.</p></div>', unsafe_allow_html=True)
with second:
    st.markdown('<div class="info-card"><h4>2. Index</h4><p>Turn your sources into a searchable knowledge base.</p></div>', unsafe_allow_html=True)
with third:
    st.markdown('<div class="info-card"><h4>3. Ask</h4><p>Get focused answers based only on your document context.</p></div>', unsafe_allow_html=True)

st.markdown('<p class="chat-label">Conversation</p>', unsafe_allow_html=True)

if not st.session_state.messages:
    st.info("Start by uploading and indexing documents, then ask a question below.")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = st.chat_input("Ask a question about your documents...")
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching your documents..."):
            try:
                if search_scope == "Choose documents" and not selected_files:
                    answer = "Please select at least one document in the sidebar."
                else:
                    answer = ask_question(question, filenames=selected_files)
            except Exception as error:
                answer = f"I couldn't answer that question: {error}"
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
