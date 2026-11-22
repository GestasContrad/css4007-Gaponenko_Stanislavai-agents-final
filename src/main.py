import json
import sys
from typing import Optional

from src.llm_client import LLMClient
from src.tools import extract_key_metrics, get_paper_details, search_papers


def run_core_demo(query: str = "RAG", year_from: int = 2024, paper_id: str = "P004") -> None:
    """Demonstrates core Week 12 functionality: repository tools + validated structured LLM output."""
    print(f"=== 1. Searching papers (query='{query}', year_from={year_from}) ===")
    search_output = search_papers(query=query, year_from=year_from)
    print(json.dumps(search_output, indent=2))

    print(f"\n=== 2. Retrieving details & metrics for '{paper_id}' ===")
    details = get_paper_details(paper_id)
    metrics = extract_key_metrics(paper_id)

    if "error" in details:
        print(f"[Repository Error] {details['error']}")
        return

    print(f"Title: {details['title']} ({details['year']}, {details['venue']})")
    print(f"Metrics: {metrics.get('metrics', {})}")

    print("\n=== 3. Generating Pydantic-validated structured LLM analysis ===")
    try:
        client = LLMClient()
    except ValueError as err:
        print(f"[Configuration Error] {err}")
        sys.exit(1)

    analysis = client.generate_structured_analysis(details, metrics)
    if analysis["success"]:
        print("Validated Structured Output:")
        print(json.dumps(analysis["data"], indent=2))
    else:
        print(f"[LLM Error] {analysis['error']}")


def run_single_prompt(prompt: Optional[str] = None) -> None:
    """Fallback single prompt execution from Week 11."""
    client = LLMClient()
    result = client.generate_response(prompt or "Explain RAG in 2 sentences.")
    if result["success"]:
        print(result["content"])
    else:
        print(f"[Error] {result['error']}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--ask":
        custom_prompt = " ".join(sys.argv[2:]).strip()
        run_single_prompt(custom_prompt)
    else:
        target_id = sys.argv[1] if len(sys.argv) > 1 else "P004"
        run_core_demo(paper_id=target_id)