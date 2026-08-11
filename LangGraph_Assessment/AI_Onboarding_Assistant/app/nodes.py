import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from .rag import build_retriever
from .state import State
from pathlib import Path

load_dotenv()

# LLM

llm=ChatGroq(model="llama-3.3-70b-versatile",temperature=0.4)

# Retriever

retriever = build_retriever()

# NODE 1: VALIDATION

def validate_node(state: State):

    if not state["question"].strip():
        return {
            "answer": "Question cannot be empty.",
            "query_type": "invalid"
        }

    if state["role"] not in ["employee", "manager", "it_admin", "hr"]:
        return {
            "answer": "Invalid user role.",
            "query_type": "invalid"
        }

    return {}

# NODE 2: RETRIEVAL

def retrieve_node(state: State):

    documents = retriever.invoke(state["question"])

    context = []
    citations = []

    for doc in documents:
        context.append(doc.page_content)
        citations.append(Path(doc.metadata.get("source", "unknown")).name)

    return {
        "retrieved_context": context,
        "citations": citations
    }

# NODE 3: CLASSIFICATION

def classifier_node(state: State):

    question = state["question"]

    prompt =f"""
Classify this user request into exactly one category:

information
account_access
unsupported

information = questions seeking onboarding-related knowledge, guidance, or instructions.
Examples: how to set up a laptop, how to install software, company policies,
where to find documents, how benefits work, IT setup steps, general how-to questions
about onboarding.

account_access = requests to create, grant, enable, or request access to a system,
account, or tool (e.g. "give me VPN access", "create my email account").

unsupported = requests unrelated to onboarding entirely (e.g. personal advice,
unrelated topics, requests outside company processes).

If the question is a how-to or informational question related to onboarding,
even loosely, classify it as "information", not "unsupported".

Return only the category name.

Question: {question}
"""

    response = llm.invoke(prompt)

    category = response.content.strip().lower()

    if category not in ["information", "account_access", "unsupported"]:
        category = "unsupported"

    result = {
        "query_type": category
    }

    if category == "unsupported":
        result["answer"] = "This request is outside the scope of onboarding support. Please contact HR or IT directly."

    return result

# NODE 4: GROUNDING CHECK

def grounding_node(state: State):
    context = state.get("retrieved_context", [])
    if not context:
        return {
            "answer": "I don't have enough information in the approved documents to answer that."
        }
    return {}

# NODE 5: GENERATE ANSWER

def generate_node(state: State):

    if state.get("answer"):
        return {}
    context = "\n\n".join(state["retrieved_context"])

    prompt = f"""
Answer the question using ONLY the context below.

If the answer is not in the context, say:
I don't have enough information to answer this.

Context:
{context}

Question:
{state["question"]}
"""

    response = llm.invoke(prompt)

    return {
        "answer": response.content.strip()
    }

# NODE 6: APPROVAL

def approval_node(state: State):

    if state["approval_status"] == "approved":
        return {}

    if state["approval_status"] == "rejected":
        return {
            "answer": "Access rejected. No action was executed."
        }

    return {
        "answer": "Approval required. No action was executed."
    }

# NODE 7: MOCK TOOL

def access_tool_node(state: State):

    result = {
        "status": "success",
        "message": f"Mock VPN access requested for {state['role']}"
    }

    return {
        "tool_result": result,
        "answer": result["message"]
    }

# NODE 8: FINAL RESPONSE

def final_node(state: State):

    answer = state["answer"]

    if state.get("query_type") == "information" and state["citations"]:
        answer += "\nSources: " + ", ".join(state["citations"])

    return {
        "answer": answer
    }