import json
from pathlib import Path
from typing import Any, Dict, List

from pydantic import ValidationError
from src.schemas import PaperDetails, PaperMetrics, PaperSummary, SearchResult, validate_tool_args

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "papers.json"


def load_papers() -> List[Dict[str, Any]]:
    """Loads the local academic paper dataset from JSON."""
    if not DATA_PATH.exists():
        return []
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("Paper dataset must be a JSON list of paper objects.")
    return data


def search_papers(query: str, year_from: int = 2020) -> Dict[str, Any]:
    """Searches papers by keyword query and minimum publication year."""
    is_valid, error = validate_tool_args("search_papers", {"query": query, "year_from": year_from})
    if not is_valid:
        return {"error": error}

    q = query.strip().lower()
    matched: List[PaperSummary] = []

    try:
        papers = load_papers()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return {"error": f"Failed to load paper repository: {exc}"}

    for paper in papers:
        authors_text = " ".join(paper.get("authors", []))
        searchable_text = (
            f"{paper.get('title', '')} {paper.get('abstract', '')} "
            f"{paper.get('topic', '')} {authors_text}"
        ).lower()
        if q in searchable_text and paper.get("year", 0) >= year_from:
            matched.append(
                PaperSummary(
                    paper_id=paper["paper_id"],
                    title=paper["title"],
                    authors=paper["authors"],
                    year=paper["year"],
                    topic=paper["topic"],
                )
            )

    try:
        validated = SearchResult(
            query=query.strip(),
            year_from=year_from,
            count=len(matched),
            results=matched,
        )
        return validated.model_dump()
    except ValidationError as exc:
        return {"error": f"Output validation failed: {exc}"}


def get_paper_details(paper_id: str) -> Dict[str, Any]:
    """Retrieves full bibliographic details and abstract for a specific paper ID."""
    is_valid, error = validate_tool_args("get_paper_details", {"paper_id": paper_id})
    if not is_valid:
        return {"error": error}

    pid = paper_id.strip().upper()
    try:
        papers = load_papers()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return {"error": f"Failed to load paper repository: {exc}"}

    for paper in papers:
        if paper.get("paper_id", "").upper() == pid:
            try:
                validated = PaperDetails(
                    paper_id=paper["paper_id"],
                    title=paper["title"],
                    authors=paper["authors"],
                    year=paper["year"],
                    venue=paper["venue"],
                    topic=paper["topic"],
                    abstract=paper["abstract"],
                )
                return validated.model_dump()
            except ValidationError as exc:
                return {"error": f"Paper record validation failed: {exc}"}

    return {"error": f"Paper with ID '{pid}' was not found in the repository."}


def extract_key_metrics(paper_id: str) -> Dict[str, Any]:
    """Extracts experimental datasets, metrics, and main findings for a paper ID."""
    is_valid, error = validate_tool_args("extract_key_metrics", {"paper_id": paper_id})
    if not is_valid:
        return {"error": error}

    pid = paper_id.strip().upper()
    try:
        papers = load_papers()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return {"error": f"Failed to load paper repository: {exc}"}

    for paper in papers:
        if paper.get("paper_id", "").upper() == pid:
            try:
                validated = PaperMetrics(
                    paper_id=paper["paper_id"],
                    title=paper["title"],
                    datasets=paper.get("datasets", []),
                    metrics=paper.get("metrics", {}),
                    main_finding=paper.get("main_finding", "No finding recorded."),
                )
                return validated.model_dump()
            except ValidationError as exc:
                return {"error": f"Metrics validation failed: {exc}"}

    return {"error": f"Metrics unavailable: Paper with ID '{pid}' was not found."}