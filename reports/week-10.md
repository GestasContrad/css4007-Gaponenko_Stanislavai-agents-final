# Semester Week 10 Progress Report

## Completed Work

- Forked and cloned the course repository, configured the local PyCharm development environment, and selected the C-level (Tool-Using AI Agent) track.
- Defined the project scope and architecture in `reports/proposal.md` for the **Scholarly Research Paper & Document Finder Agent** powered by the OpenAI API (`gpt-4o-mini`).
- Created the initial structured dataset of academic papers in `data/papers.json` and implemented foundational tool functions (`search_papers`, `get_paper_details`, `extract_key_metrics`) with input validation in `src/tools.py`.

## Important Commits

- Commit hash: `1d88abe`
  - Description: Complete C-level project proposal for Research Paper Finder agent (`reports/proposal.md`).
  - Link: `https://github.com/GestasContrad/css4007-Gaponenko_Stanislavai-agents-final/commit/1d88abe`
- Commit hash: `7c4279f`
  - Description: Add initial academic paper dataset (`data/papers.json`), `requirements.txt`, and tool functions (`src/tools.py`).
  - Link: `https://github.com/GestasContrad/css4007-Gaponenko_Stanislavai-agents-final/commit/7c4279f`

## Current Functionality

- The project currently includes a curated JSON dataset of 5 AI/NLP research papers (`P001`–`P005`) and three local Python functions capable of searching papers by keyword and publication year, retrieving full metadata/abstracts, and extracting benchmark metrics with argument validation.

## Problems Encountered

- Needed to design a repository data structure that supports deterministic testing for C-level tool calls without relying on unstable external web scrapers or rate-limited third-party academic APIs.

## Solutions

- Designed a self-contained local JSON catalog (`data/papers.json`) paired with strict argument validation in `src/tools.py` so every tool call, missing ID error, and metric lookup is reproducible during automated tests and live defense.

## What I Learned

- Learned how C-level tool-using agent architectures separate deterministic data retrieval functions from LLM reasoning and how to specify clean function signatures before registering OpenAI tool schemas.

## Next Week

- Implement the OpenAI API client wrapper (`src/llm_client.py`) using `gpt-4o-mini`, configure `.env` loading, implement the first working LLM request-response pipeline, and add basic CLI interaction for Week 11.