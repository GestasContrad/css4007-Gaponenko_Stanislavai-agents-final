# Project Proposal — Semester Week 10

## Project Title

Scholarly Research Paper & Document Finder Agent

## Problem Description

Students and researchers spend significant time manually filtering academic papers by publication year, topic, and experimental benchmarks across scattered repositories. Furthermore, standard LLM chat interfaces often hallucinate paper titles, authors, publication dates, or reported evaluation metrics when answering literature review questions. This project solves that problem by grounding an OpenAI-powered conversational agent in deterministic search and metadata-extraction tools over a structured repository of computer science and artificial intelligence papers.

## Target Users

University students, teaching assistants, and academic researchers who need quick, verifiable answers about scientific publications, methodologies, and benchmark metrics without hallucinations.

## Selected Difficulty

C — Intermediate (Tool-Using AI Agent)

## Expected Functionality

- Natural language query understanding for academic literature requests.
- Dynamic LLM-driven tool selection using the OpenAI Function Calling API.
- Multi-criteria paper search by topic keywords and minimum publication year.
- Full metadata lookup by unique paper identifier (`paper_id`).
- Structured extraction of experimental metrics, datasets, and baseline comparisons for specific papers.
- Direct conversational responses for general theoretical questions that do not require tool execution.
- Strict input/argument validation, execution logging, and graceful handling of missing papers or API errors.

## Proposed Functions

1. `search_papers(query: str, year_from: int = 2020) -> list[dict]`
   - **Purpose:** Searches the local academic catalog for papers matching a keyword query in the title, abstract, or tags, filtered by minimum publication year.
   - **Inputs:** `query` (non-empty string keyword), `year_from` (integer between 1990 and 2026, optional, defaults to 2020).
   - **Expected Output:** List of matching paper summary dictionaries (`paper_id`, `title`, `authors`, `year`, `topic`).
   - **Dependencies:** Python standard library (`json`, `pathlib`) and local catalog `data/papers.json`.

2. `get_paper_details(paper_id: str) -> dict`
   - **Purpose:** Retrieves the complete bibliographic record and abstract for a specific paper identifier.
   - **Inputs:** `paper_id` (string formatted like `"P001"`).
   - **Expected Output:** Dictionary containing full paper details (`paper_id`, `title`, `authors`, `year`, `venue`, `abstract`, `pdf_url`) or a structured error object if not found.
   - **Dependencies:** Local catalog `data/papers.json`.

3. `extract_key_metrics(paper_id: str) -> dict`
   - **Purpose:** Extracts structured experimental evaluation metrics, datasets used, and primary findings for a given paper.
   - **Inputs:** `paper_id` (string identifier).
   - **Expected Output:** Dictionary containing `paper_id`, `title`, `datasets`, `metrics` (key-value pairs of metric names and scores), and `main_finding`, or an error object if unavailable.
   - **Dependencies:** Local catalog `data/papers.json`.

4. `validate_tool_args(tool_name: str, args: dict) -> tuple[bool, str]`
   - **Purpose:** Validates LLM-supplied tool arguments before executing any Python function.
   - **Inputs:** `tool_name` (string), `args` (dictionary of parsed JSON arguments).
   - **Expected Output:** Tuple `(is_valid, error_message)`.
   - **Dependencies:** Python built-in types and `pydantic` / custom validation rules.

## Proposed Agent Tools

- `search_papers`: Exposed as an LLM tool so the agent can discover relevant papers when the user asks about a research topic or time period without knowing specific paper IDs.
- `get_paper_details`: Exposed as an LLM tool so the agent can inspect the full abstract, authors, and publication venue of a specific paper before summarizing it.
- `extract_key_metrics`: Exposed as an LLM tool so the agent can retrieve exact quantitative benchmark figures and datasets without guessing or hallucinating numbers.

## Model Selection

- **Provider & Model:** OpenAI API using `gpt-4o-mini` (configurable via `LLM_MODEL` in `.env`).
- **Integration Approach:** Official Python `openai` SDK (`chat.completions.create` with `tools` and `tool_choice="auto"`), using temperature `0.0` for deterministic tool routing and grounded responses.

## Architecture

```text
User Request
     │
     ▼
Input Validation & Prompt Construction (src/agent.py)
     │
     ▼
OpenAI LLM (`gpt-4o-mini` with registered Tool Schemas)
     │
     ├──► [No Tool Needed] ──────────────────────────────────┐
     │                                                       │
     └──► [Tool Call Requested]                              ▼
               │                                    Final Grounded Response
               ▼                                             ▲
     Argument Validator & Logger (src/tools.py)              │
               │                                             │
               ▼                                             │
     Tool Execution (`search_papers` / `get_paper_details` / `extract_key_metrics`)
               │                                             │
               └──► Tool Result JSON ──► OpenAI LLM ─────────┘
```

## Example Requests

- **Tool Call (search_papers):** "Find research papers about Retrieval-Augmented Generation published from 2024 onwards."

- **Tool Call (get_paper_details + extract_key_metrics):** "What datasets and quantitative metrics are reported in paper P002, and who are the authors?"

- **Edge Case / Unavailable Info:** "Show me the abstract and benchmark metrics for paper P999." (Agent calls tool, receives "Paper not found", and politely informs the user without inventing data).

- **No Tool Required:** "Explain the difference between zero-shot prompting and few-shot prompting in simple terms." (Agent answers directly without calling repository tools).

## Evaluation Plan

- **Unit & Functional Tests (pytest):** At least 8 automated test cases in tests/test_agent.py covering:

1. Valid keyword and year search (search_papers).

2. Valid paper metadata retrieval (get_paper_details).

3. Quantitative benchmark extraction (extract_key_metrics).

4. Direct general question answering without calling any tools.

5. Unknown paper_id handling (P999) verifying zero hallucination.

6. Invalid tool argument rejection (e.g., empty query or invalid year_from type).

7. Empty search result handling when no papers match the filter.

8. Simulated LLM API / network timeout error handling and execution logging verification.

## Weekly Milestones

- **Week 10:** Complete project proposal (reports/proposal.md), initialize Python project structure, create initial paper dataset (data/papers.json), and submit reports/week-10.md.

- **Week 11:** Set up OpenAI API client wrapper (src/llm_client.py), environment configuration, and first working prompt-response prototype.

- **Week 12:** Implement core repository functions (search_papers, get_paper_details, extract_key_metrics), input/output validation, and initial unit tests.

- **Week 13:** Register JSON tool schemas with OpenAI, implement automated LLM tool selection and execution dispatcher (src/agent.py).

- **Week 14:** Complete end-to-end tool-calling conversation loop, structured execution logging (logs/tool_calls.jsonl), and tool error handling.

- **Week 15:** Harden reliability against API failures, malformed JSON arguments, and edge-case user inputs; expand test suite to 8+ scenarios.

- **Week 16:** Run complete evaluation suite, analyze logs and test results, refine documentation, and complete reports/week-16.md.

- **Week 17:** Final code cleanup, reports/final-report.md, and live project defense.


