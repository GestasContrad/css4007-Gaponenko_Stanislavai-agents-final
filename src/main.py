import sys
from src.llm_client import LLMClient


def run_demo_query(prompt: str | None = None) -> None:
    """Executes a single working LLM request and prints the structured result."""
    query = prompt or (
        "Briefly explain the difference between standard Retrieval-Augmented Generation (RAG) "
        "and agentic tool use in 3 bullet points."
    )

    print(f"Initializing LLMClient...")
    try:
        client = LLMClient()
    except ValueError as err:
        print(f"[Configuration Error] {err}")
        sys.exit(1)

    print(f"Sending request to model '{client.model}'...")
    print(f"User Prompt: {query}\n" + "-" * 60)

    result = client.generate_response(query)

    if result["success"]:
        print("LLM Response:\n")
        print(result["content"])
        print("-" * 60)
        print(f"Token Usage: {result['usage']}")
    else:
        print(f"[Error] {result['error']}")


if __name__ == "__main__":
    user_arg = " ".join(sys.argv[1:]).strip() if len(sys.argv) > 1 else None
    run_demo_query(user_arg)