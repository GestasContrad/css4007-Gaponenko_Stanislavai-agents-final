import json
from unittest.mock import MagicMock, patch

from src.llm_client import LLMClient
from src.schemas import validate_tool_args
from src.tools import extract_key_metrics, get_paper_details, search_papers


def test_search_papers_valid_query_and_year():
    result = search_papers(query="RAG", year_from=2024)
    assert "error" not in result
    assert result["count"] >= 2
    paper_ids = [p["paper_id"] for p in result["results"]]
    assert "P004" in paper_ids
    assert "P008" in paper_ids
    assert all(p["year"] >= 2024 for p in result["results"])


def test_search_papers_empty_match():
    result = search_papers(query="quantum_teleportation_xyz", year_from=2020)
    assert "error" not in result
    assert result["count"] == 0
    assert result["results"] == []


def test_get_paper_details_valid_id():
    result = get_paper_details("P002")
    assert "error" not in result
    assert result["paper_id"] == "P002"
    assert "ReAct" in result["title"]
    assert result["year"] == 2023


def test_get_paper_details_not_found():
    result = get_paper_details("P999")
    assert "error" in result
    assert "not found" in result["error"].lower()


def test_extract_key_metrics_valid_id():
    result = extract_key_metrics("P004")
    assert "error" not in result
    assert result["paper_id"] == "P004"
    assert "PopQA Accuracy" in result["metrics"]
    assert len(result["datasets"]) > 0


def test_validate_tool_args_rejects_invalid_inputs():
    valid_q, err_q = validate_tool_args("search_papers", {"query": "   ", "year_from": 2022})
    assert not valid_q and "query" in err_q

    valid_y, err_y = validate_tool_args("search_papers", {"query": "RAG", "year_from": "2024"})
    assert not valid_y and "year_from" in err_y

    valid_id, err_id = validate_tool_args("get_paper_details", {"paper_id": "INVALID"})
    assert not valid_id and "paper_id" in err_id

    valid_tool, err_tool = validate_tool_args("delete_database", {})
    assert not valid_tool and "Unknown tool" in err_tool


def test_llm_structured_analysis_valid_json_passes_schema():
    mock_payload = {
        "paper_id": "P004",
        "title": "Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection",
        "research_area": "Retrieval-Augmented Generation",
        "key_contributions": [
            "Introduces adaptive on-demand retrieval.",
            "Uses reflection tokens to critique generated outputs.",
        ],
        "reported_metrics": {"PopQA Accuracy": "55.8%"},
        "practical_takeaway": "Self-reflection improves factual accuracy over standard RAG.",
    }

    mock_response = MagicMock()
    mock_response.model = "gpt-4o-mini"
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps(mock_payload)

    with patch("src.llm_client.OpenAI") as mock_openai_cls:
        mock_instance = mock_openai_cls.return_value
        mock_instance.chat.completions.create.return_value = mock_response

        client = LLMClient(api_key="test-key", model="gpt-4o-mini")
        details = get_paper_details("P004")
        metrics = extract_key_metrics("P004")
        res = client.generate_structured_analysis(details, metrics)

        assert res["success"] is True
        assert res["error"] is None
        assert res["data"]["paper_id"] == "P004"
        assert len(res["data"]["key_contributions"]) == 2


def test_llm_structured_analysis_handles_malformed_json():
    mock_response = MagicMock()
    mock_response.model = "gpt-4o-mini"
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "{not valid json"

    with patch("src.llm_client.OpenAI") as mock_openai_cls:
        mock_instance = mock_openai_cls.return_value
        mock_instance.chat.completions.create.return_value = mock_response

        client = LLMClient(api_key="test-key", model="gpt-4o-mini")
        details = get_paper_details("P004")
        metrics = extract_key_metrics("P004")
        res = client.generate_structured_analysis(details, metrics)

        assert res["success"] is False
        assert res["data"] is None
        assert "invalid JSON" in res["error"]