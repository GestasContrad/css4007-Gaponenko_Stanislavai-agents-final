import json
from pathlib import Path
from typing import Any

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "papers.json"


def load_papers() -> list[dict[str, Any]]:
    """Loads the local academic paper dataset from JSON."""
    if not DATA_PATH.exists():
        return []
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def search_papers(query: str, year_from: int = 2020) -> dict[str, Any]:
    """Searches papers by keyword query and minimum publication year."""
    if not isinstance(query, str) or not query.strip():
        return {"error": "Invalid argument: 'query' must be a non-empty string."}
    if not isinstance(year_from, int) or year_from < 1900 or year_from > 2030:
        return {"error": "Invalid argument: 'year_from' must be a valid year between 1900 and 2030."}

    q = query.strip().lower()
    results = []
    for paper in load_papers():
        searchable_text = f"{paper.get('title', '')} {paper.get('abstract', '')} {paper.get('topic', '')}".lower()
        if q in searchable_text and paper.get("year", 0) >= year_from:
            results.append({
                "paper_id": paper["paper_id"],
                "title": paper["title"],
                "authors": paper["authors"],
                "year": paper["year"],
                "topic": paper["topic"],
            })

    return {
        "query": query,
        "year_from": year_from,
        "count": len(results),
        "results": results,
    }


def get_paper_details(paper_id: str) -> dict[str, Any]:
    """Retrieves full bibliographic details and abstract for a specific paper ID."""
    if not isinstance(paper_id, str) or not paper_id.strip():
        return {"error": "Invalid argument: 'paper_id' must be a non-empty string."}

    pid = paper_id.strip().upper()
    for paper in load_papers():
        if paper.get("paper_id", "").upper() == pid:
            return {
                "paper_id": paper["paper_id"],
                "title": paper["title"],
                "authors": paper["authors"],
                "year": paper["year"],
                "venue": paper["venue"],
                "topic": paper["topic"],
                "abstract": paper["abstract"],
            }

    return {"error": f"Paper with ID '{paper_id}' was not found in the repository."}


def extract_key_metrics(paper_id: str) -> dict[str, Any]:
    """Extracts experimental datasets, metrics, and main findings for a paper ID."""
    if not isinstance(paper_id, str) or not paper_id.strip():
        return {"error": "Invalid argument: 'paper_id' must be a non-empty string."}

    pid = paper_id.strip().upper()
    for paper in load_papers():
        if paper.get("paper_id", "").upper() == pid:
            return {
                "paper_id": paper["paper_id"],
                "title": paper["title"],
                "datasets": paper.get("datasets", []),
                "metrics": paper.get("metrics", {}),
                "main_finding": paper.get("main_finding", "No finding recorded."),
            }

    return {"error": f"Metrics unavailable: Paper with ID '{paper_id}' was not found."}