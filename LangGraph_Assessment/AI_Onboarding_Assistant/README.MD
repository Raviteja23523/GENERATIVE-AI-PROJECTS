AI Onboarding Assistant

A simple AI-powered employee onboarding assistant built with LangGraph, LangChain, Groq, FAISS, and Hugging Face embeddings.

Features

Validates user questions and roles

Searches approved .md onboarding documents using RAG

Uses FAISS for vector search

Classifies requests into:

information

account_access

unsupported

Generates answers using retrieved context only

Checks whether retrieved context is available

Requires approval before account-access actions

Uses a mock VPN access tool

Returns source documents with answers

Project Structure

AI_Onboarding_Assistant/
│
├── data/
│   ├── onboarding_guide.md
│   ├── support_escalation_guide.md
│   └── product_faq.md
│
├── app/
│   ├── main.py
│   ├── state.py
│   ├── rag.py
│   ├── nodes.py
│   └── graph.py
│
├── .env
├── requirements.txt
└── README.md

Workflow

START
  ↓
VALIDATE
  ↓
RETRIEVE
  ↓
GROUNDING
  ↓
CLASSIFY
  ├── information → GENERATE → FINAL
  ├── unsupported → FINAL
  └── account_access → APPROVAL
                         ├── rejected → FINAL
                         └── approved → TOOL → FINAL

Nodes

1. Validate

Checks that the question is not empty and that the role is valid.

Allowed roles:

employee

manager

it_admin

hr

2. Retrieve

Loads .md files from the data folder, splits them into chunks, creates embeddings, and searches them using FAISS.

3. Grounding

Checks whether retrieved context is available. If no context is found, the assistant does not generate an answer.

4. Classifier

Classifies the user's request as information, account_access, or unsupported.

5. Generate

Generates an answer using only the retrieved onboarding context.

6. Approval

Checks the approval status before an account-access request can continue.

7. Access Tool

A mock tool that simulates submitting a VPN access request. No real account or system is changed.

8. Final

Combines the generated answer and source citations into the final response.

RAG Process

The assistant uses the following RAG pipeline:

Markdown files
     ↓
TextLoader
     ↓
Text Splitting
     ↓
Hugging Face Embeddings
     ↓
FAISS Vector Store
     ↓
Retriever
     ↓
Relevant document chunks

The embedding model is:

sentence-transformers/all-MiniLM-L6-v2

The retriever returns the top 4 relevant chunks.

Requirements

Install the required packages:

pip install -r requirements.txt

You also need a Groq API key.

Create a .env file:

GROQ_API_KEY=your_groq_api_key

Run the Application

Run from the project root:

python -m app.main

The application asks for:

Question:
Role:
Approval (approved/rejected):

Type exit to stop the application.

Example

Information request

Question: How do I set up my laptop?
Role: employee
Approval: approved

The request follows:

validate → retrieve → grounding → classify → generate → final

Account access request

Question: I need VPN access.
Role: employee
Approval: approved

The request follows:

validate → retrieve → grounding → classify
→ approval → tool → final

The tool returns a mock result such as:

Mock VPN access requested for employee

Rejected access request

Question: I need VPN access.
Role: employee
Approval: rejected

The tool is not executed.

Safety

Answers are restricted to the approved onboarding documents.

The assistant does not intentionally use outside knowledge for information answers.

Unsupported questions are not answered from general knowledge.

Account-access actions require approval.

The access tool is only a mock tool and does not make real changes.

Testing

Recommended test cases:

Test

Expected Result

How do I set up my laptop?

Information answer + sources

How do I connect to the company VPN?

Information answer + sources

I need VPN access. + approved

Mock tool executes

I need VPN access. + rejected

No tool execution

What is the weather today?

Unsupported

Empty question

Validation error

Invalid role

Validation error

Technologies

Python

LangGraph

LangChain

Groq

FAISS

Hugging Face Embeddings

Sentence Transformers

Markdown knowledge base



run project
=================================================================
   1.python -m app.main
   2.python -m app.Python_ui
