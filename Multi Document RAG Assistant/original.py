"""Ingest documents into Chroma and answer questions using the stored content."""

import argparse
from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.document_loaders import (
    CSVLoader,
    Docx2txtLoader,
    PyPDFLoader,
    TextLoader,
)
from langchain_core.prompts import ChatPromptTemplate
from langchain_mistralai import ChatMistralAI
from langchain_groq import GroqEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


load_dotenv()

DB_DIRECTORY = "chroma_db1"
EMBEDDING_MODEL = "mixedbread-ai/mxbai-embed-large"
LLM_MODEL = "mistral-small-2506"


def get_vector_store():
    """Open the persistent Chroma database used for both ingestion and retrieval."""
    embedding_model = GroqEmbeddings(model=EMBEDDING_MODEL)
    return Chroma(
        persist_directory=DB_DIRECTORY,
        embedding_function=embedding_model,
    )


def load_document(file_path):
    """Load a supported document type into LangChain Document objects."""
    extension = Path(file_path).suffix.lower()
    loaders = {
        ".pdf": PyPDFLoader,
        ".docx": Docx2txtLoader,
        ".txt": TextLoader,
        ".csv": CSVLoader,
    }

    if extension not in loaders:
        raise ValueError(f"Unsupported file type: {extension}")

    return loaders[extension](file_path).load()


def ingest_documents(file_paths):
    """Chunk documents, create embeddings, and add them to the Chroma database."""
    documents = []
    for file_path in file_paths:
        print(f"Loading: {Path(file_path).name}")
        loaded_documents = load_document(file_path)
        for document in loaded_documents:
            document.metadata["filename"] = Path(file_path).name
            document.metadata["file_type"] = Path(file_path).suffix.lower()
        documents.extend(loaded_documents)

    print("Pages:", len(documents))
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(documents)
    print("Chunks:", len(chunks))

    vector_store = get_vector_store()
    batch_size = 50
    for start in range(0, len(chunks), batch_size):
        batch = chunks[start : start + batch_size]
        vector_store.add_documents(batch)
        print(f"Added {start + len(batch)}/{len(chunks)} chunks")

    print("Done!")
    return vector_store


def remove_documents(filenames):
    """Remove all Chroma chunks that belong to the supplied source filenames."""
    if not filenames:
        return 0

    vector_store = get_vector_store()
    stored = vector_store.get(where={"filename": {"$in": filenames}}, include=[])
    document_ids = stored.get("ids", [])
    if document_ids:
        vector_store.delete(ids=document_ids)
    return len(document_ids)


def create_rag(filenames=None):
    """Create a retriever, optionally restricted to selected source filenames."""
    vector_store = get_vector_store()
    search_kwargs = {"k": 4, "fetch_k": 10, "lambda_mult": 0.5}
    if filenames:
        search_kwargs["filter"] = {"filename": {"$in": filenames}}

    retriever = vector_store.as_retriever(
        search_type="mmr",
        search_kwargs=search_kwargs,
    )
    print("Vector Count:", vector_store._collection.count())

    llm=ChatMistralAI(model=LLM_MODEL)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a helpful document assistant. Use only the provided context.

Give a well-structured, detailed answer:
1. Start with a direct answer.
2. Use short headings and bullet points when they improve readability.
3. Explain important details clearly, but do not invent information.
4. End with a **Sources** section listing the document filenames you used.

If the answer is not present in the context, say exactly:
\"I could not find the answer in the document\"""",
            ),
            ("human", "Context: {context}\n\nQuestion: {question}"),
        ]
    )
    return retriever, llm, prompt


def ask_question(question, filenames=None):
    """Retrieve relevant chunks from all or selected documents and answer a question."""
    retriever, llm, prompt = create_rag(filenames)
    documents = retriever.invoke(question)
    context = "\n\n".join(
        f"Source filename: {document.metadata.get('filename', 'Unknown')}\n"
        f"{document.page_content}"
        for document in documents
    )
    final_prompt = prompt.invoke({"context": context, "question": question})
    return llm.invoke(final_prompt).content


def main():
    parser = argparse.ArgumentParser(description="Ingest files and query the RAG database.")
    parser.add_argument("--ingest", nargs="+", metavar="FILE", help="Files to add to Chroma")
    parser.add_argument("--question", help="Question to ask about ingested files")
    args = parser.parse_args()

    if args.ingest:
        ingest_documents(args.ingest)
    if args.question:
        print(ask_question(args.question))
    if not args.ingest and not args.question:
        parser.print_help()


if __name__ == "__main__":
    main()
