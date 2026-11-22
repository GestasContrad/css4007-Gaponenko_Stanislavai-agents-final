# Semester Week 12 Progress Report

## Completed Work

- Expanded the local academic dataset in `data/papers.json` from 5 to 10 peer-reviewed AI/NLP research papers (`P001`–`P010`) covering RAG, AI agents, tool use, evaluation benchmarks, and alignment.
- Created `src/schemas.py` with Pydantic v2 data models (`PaperSummary`, `SearchResult`, `PaperDetails`, `PaperMetrics`, `StructuredPaperAnalysis`) and centralized argument validation (`validate_tool_args`).
- Refactored core repository functions (`search_papers`, `get_paper_details`, `extract_key_metrics`) in `src/tools.py` to enforce strict input validation and schema-validated outputs.
- Extended `LLMClient` in `src/llm_client.py` with `generate_structured_analysis` using OpenAI JSON mode (`response_format={"type": "json_object"}`) and Pydantic validation, and updated `src/main.py` to demonstrate the end-to-end core workflow.
- Upgraded the project interpreter to Python 3.14, added `pytest.ini`, and implemented an initial unit test suite in `tests/test_core.py` (8 passing test cases).

## Important Commits

- Commit hash: `7c0d87d`
  - Description: Add Pydantic schemas, centralized tool argument validation (`src/schemas.py`), updated `src/tools.py`, and expanded `data/papers.json`.
  - Link: `https://github.com/GestasContrad/css4007-Gaponenko_Stanislavai-agents-final/commit/7c0d87d`
- Commit hash: `c02912e`
  - Description: Implement validated structured JSON analysis in `src/llm_client.py` and core demo workflow in `src/main.py`.
  - Link: `https://github.com/GestasContrad/css4007-Gaponenko_Stanislavai-agents-final/commit/c02912e`
- Commit hash: `5c70bce`
  - Description: Add `pytest.ini` configuration and initial `pytest` unit test suite (`tests/test_core.py`) covering core functions and structured output validation.
  - Link: `https://github.com/GestasContrad/css4007-Gaponenko_Stanislavai-agents-final/commit/5c70bce`

## Current Functionality

- The core application searches papers by keyword, author, or topic with year filtering; retrieves verified bibliographic metadata and benchmark metrics; validates all tool inputs and outputs via Pydantic; generates schema-validated structured JSON paper summaries using OpenAI `gpt-4o-mini`; and passes all 8 automated `pytest` tests.

## Problems Encountered

- Running the codebase initially on Python 3.8 caused runtime type annotation incompatibility errors (`TypeError` on union types).
- Running `pytest -v` directly triggered `ModuleNotFoundError: No module named 'src'` because the project root directory was not automatically added to `sys.path`.

## Solutions

- Switched the PyCharm project virtual environment to Python 3.14 and standardized `typing` annotations across `src/` modules.
- Added `pytest.ini` in the repository root with `pythonpath = .` and `testpaths = tests`, after which all 8 tests collected and passed cleanly.

## What I Learned

- Learned how to combine OpenAI JSON mode with Pydantic v2 schema validation to guarantee structured, hallucination-free outputs, configure `pytest` import resolution cleanly via `pytest.ini`, and isolate LLM calls with `unittest.mock` for deterministic testing.

## Next Week

- Implement OpenAI Function Calling tool schemas (`tools` definitions), automated LLM tool selection, and a real tool execution dispatcher in `src/agent.py` for Week 13 (Tool Integration).