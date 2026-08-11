from .graph import build_graph

VALID_ROLES = ["employee", "manager", "it_admin", "hr"]


def main():

    graph = build_graph()

    role_prompt = f"Role ({'/'.join(VALID_ROLES)}): "

    while True:

        question = input("\nQuestion: ").strip()

        if question.lower() == "exit":
            break

        role = input(role_prompt).strip().lower()

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

        result = graph.invoke(state)

        # If this turned out to be an account_access request, approval_node
        # already ran once with "pending" (so no action was executed) —
        # now ask for a real approval decision and re-run just that part.
        if result.get("query_type") == "account_access":
            approval = input("Approval (approved/rejected): ").strip().lower()
            state["approval_status"] = approval
            state["query_type"] = "account_access"
            result = graph.invoke(state)

        answer = result.get("answer") or "No answer was generated."

        print("\nAnswer:", answer)

        tool_result = result.get("tool_result")
        if tool_result:
            print("Tool result:", tool_result)


if __name__ == "__main__":
    main()