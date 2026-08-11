import tkinter as tk
from tkinter import ttk, scrolledtext

from .graph import build_graph


ROLES = [
    "employee",
    "manager",
    "it_admin",
    "hr"
]


graph = build_graph()


def ask_question():

    question = question_box.get().strip()
    role = role_box.get()

    if not question:
        output.insert(
            tk.END,
            "\nQuestion cannot be empty.\n"
        )
        return

    state = {
        "question": question,
        "role": role,
        "retrieved_context": [],
        "citations": [],
        "query_type": "",
        "answer": "",
        "approval_status": "pending",
        "tool_result": {}
    }

    try:

        output.insert(
            tk.END,
            "\nProcessing...\n"
        )

        result = graph.invoke(state)

        # Account access
        if result.get("query_type") == "account_access":

            approval = approval_box.get()

            state["approval_status"] = approval
            state["query_type"] = "account_access"

            result = graph.invoke(state)

        # Answer
        answer = result.get(
            "answer",
            "No answer generated."
        )

        output.insert(
            tk.END,
            "\nAnswer:\n"
        )

        output.insert(
            tk.END,
            answer + "\n"
        )

        # Sources
        citations = result.get(
            "citations",
            []
        )

        if citations:

            output.insert(
                tk.END,
                "\nSources:\n"
            )

            for source in citations:

                output.insert(
                    tk.END,
                    f"- {source}\n"
                )

        # Tool result
        tool_result = result.get(
            "tool_result",
            {}
        )

        if tool_result:

            output.insert(
                tk.END,
                "\nTool Result:\n"
            )

            output.insert(
                tk.END,
                str(tool_result) + "\n"
            )

        output.insert(
            tk.END,
            "\n" + "-" * 60 + "\n"
        )

    except Exception as e:

        output.insert(
            tk.END,
            f"\nError: {type(e).__name__}: {e}\n"
        )


def clear_output():

    output.delete(
        "1.0",
        tk.END
    )


# --------------------------------
# WINDOW
# --------------------------------

window = tk.Tk()

window.title(
    "AI Onboarding Assistant"
)

window.geometry(
    "800x650"
)


# --------------------------------
# TITLE
# --------------------------------

title = tk.Label(
    window,
    text="AI ONBOARDING ASSISTANT",
    font=("Arial", 22, "bold")
)

title.pack(pady=15)


# --------------------------------
# ROLE
# --------------------------------

role_frame = tk.Frame(window)

role_frame.pack(pady=5)

tk.Label(
    role_frame,
    text="Role:"
).pack(side=tk.LEFT)

role_box = ttk.Combobox(
    role_frame,
    values=ROLES,
    state="readonly",
    width=20
)

role_box.set("employee")

role_box.pack(
    side=tk.LEFT,
    padx=10
)


# --------------------------------
# QUESTION
# --------------------------------

tk.Label(
    window,
    text="Question:"
).pack(
    anchor="w",
    padx=25
)

question_box = tk.Entry(
    window,
    width=90
)

question_box.pack(
    padx=25,
    pady=5
)


# --------------------------------
# APPROVAL
# --------------------------------

approval_frame = tk.Frame(window)

approval_frame.pack(pady=5)

tk.Label(
    approval_frame,
    text="Approval:"
).pack(side=tk.LEFT)

approval_box = ttk.Combobox(
    approval_frame,
    values=[
        "pending",
        "approved",
        "rejected"
    ],
    state="readonly",
    width=20
)

approval_box.set("pending")

approval_box.pack(
    side=tk.LEFT,
    padx=10
)


# --------------------------------
# BUTTONS
# --------------------------------

button_frame = tk.Frame(window)

button_frame.pack(pady=10)


tk.Button(
    button_frame,
    text="Ask",
    width=15,
    command=ask_question
).pack(
    side=tk.LEFT,
    padx=5
)


tk.Button(
    button_frame,
    text="Clear",
    width=15,
    command=clear_output
).pack(
    side=tk.LEFT,
    padx=5
)


# --------------------------------
# OUTPUT
# --------------------------------

output = scrolledtext.ScrolledText(
    window,
    width=95,
    height=25,
    wrap=tk.WORD
)

output.pack(
    padx=20,
    pady=10,
    fill=tk.BOTH,
    expand=True
)


# --------------------------------
# START WINDOW
# --------------------------------

window.mainloop()