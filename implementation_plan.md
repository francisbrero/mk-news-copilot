# Implementation Plan: MK News Copilot

This document outlines the steps to build the MK News Copilot application as defined in the [PRD.md](PRD.md).

## Overall Approach

We will build the application iteratively, starting with the core data structures and ingestion, followed by AI integration, API development, and finally testing/refinement. We'll use Python with FastAPI for the backend API and local JSON files for data storage as specified.

## Milestones

### Milestone 1: Foundation & Data Setup

*   **Tasks:**
    *   Initialize Git repository.
    *   Set up Python virtual environment (`venv`).
    *   Create `requirements.txt` listing initial dependencies (e.g., `fastapi`, `uvicorn`, `requests`, `python-dotenv`, `openai`, `pydantic`).
    *   Define Pydantic models for `NewsArticle` and `Company` corresponding to `news.json` and `companies.json` schemas.
    *   Create utility functions (`data_utils.py`) for atomic read/write operations on JSON files to prevent data corruption.
    *   Create initial empty `data/news.json` and `data/companies.json` files.
    *   Set up `.env` file for environment variables (like OpenAI API key).
*   **Outcome:** Project structure is set up, data models defined, and basic file I/O utilities are ready.

### Milestone 2: Data Ingestion

*   **Tasks:**
    *   Develop `scripts/ingest.py`.
    *   Implement fetching logic for 1-2 news sources (e.g., TechCrunch RSS, a specific industry blog). Use the `requests` library.
    *   Implement basic HTML parsing if necessary (e.g., using `beautifulsoup4` - add to `requirements.txt`).
    *   Handle potential network errors and parsing issues gracefully.
    *   Map fetched data to the `NewsArticle` Pydantic model.
    *   Append new articles to `data/news.json`, ensuring duplicates are not added (e.g., by checking article URL).
*   **Outcome:** A runnable script that fetches news from selected sources and stores it in `news.json`.

### Milestone 3: AI Classification & Summarization

*   **Tasks:**
    *   Create `ai_processor.py` module.
    *   Integrate OpenAI API client using the `openai` library. Load API key from `.env`.
    *   Implement `tag_article(article_text: str) -> dict` function:
        *   Uses GPT-3.5.
        *   Identifies mentioned companies.
        *   Assigns topics from the predefined list (Fundraising, Cybersecurity Incident, etc.).
        *   Handles potential API errors.
    *   Implement `summarize_article(article_text: str) -> str` function:
        *   Uses GPT-4o.
        *   Generates a 1-2 sentence summary.
        *   Handles potential API errors.
    *   Modify `scripts/ingest.py` to call `tag_article` and `summarize_article` for each new article *after* it's initially saved, then update the article record in `data/news.json` with tags and summary.
*   **Outcome:** Ingestion script now enriches news articles with AI-generated tags and summaries.

### Milestone 4: API Implementation (FastAPI)

*   **Tasks:**
    *   Set up main FastAPI application file (`main.py`).
    *   Use Pydantic models defined in Milestone 1 for request/response validation.
    *   Define data structure for subscriptions (e.g., `data/subscriptions.json`, perhaps a simple dict mapping user ID (initially static) to lists of companies/topics). Add read/write utils.
    *   Implement API endpoints:
        *   `GET /news`: Filter by `company`, `topic`, `start_date`, `end_date`. Reads from `data/news.json`.
        *   `GET /companies`: List all or filter by name. Reads from `data/companies.json`.
        *   `POST /subscriptions`: Add a company or topic subscription for a user. Writes to `data/subscriptions.json`.
        *   `GET /subscriptions`: List subscriptions for a user. Reads from `data/subscriptions.json`.
        *   `DELETE /subscriptions`: Remove a subscription. Updates `data/subscriptions.json`.
        *   `GET /feed`: Retrieve news filtered by the user's subscriptions. Combines reading subscriptions and news data.
    *   Implement logic within endpoints to load data from JSON files.
*   **Outcome:** A functional API server that allows querying news/companies and managing basic subscriptions.

### Milestone 5: Testing & Documentation

*   **Tasks:**
    *   Add `pytest` to `requirements.txt`.
    *   Write unit tests for `data_utils.py`, `ai_processor.py` (mocking OpenAI calls), and core API endpoint logic using FastAPI's `TestClient`.
    *   Perform manual end-to-end testing: run ingestion, then query API endpoints using `curl` or a tool like Postman/Insomnia.
    *   Write/update `README.md`: Include setup instructions, how to run ingestion, how to start the API server, and basic API usage examples.
    *   Ensure FastAPI's automatic Swagger UI (`/docs`) and ReDoc (`/redoc`) documentation is generated and accessible.
*   **Outcome:** Increased confidence in code correctness, clear instructions for running and using the application.

### Milestone 6: Refinement & Future Considerations (Ongoing)

*   **Tasks:**
    *   Implement simple API key authentication (e.g., checking a static key in request headers via FastAPI dependencies).
    *   Enhance logging throughout the application (ingestion script, API).
    *   Add more news sources to `scripts/ingest.py`.
    *   Iteratively refine AI prompts based on tagging/summarization quality.
    *   Consider and document limitations of local JSON storage and potential future migration paths (e.g., SQLite, PostgreSQL).
*   **Outcome:** A more robust and production-ready (though still simple) MVP.

## Technology Stack Summary

*   **Backend:** Python 3.11, FastAPI
*   **AI/ML:** OpenAI API (GPT-3.5, GPT-4o)
*   **Data Storage:** Local JSON files
*   **Libraries:** `requests`, `openai`, `pydantic`, `uvicorn`, `python-dotenv`, `pytest` (potentially `beautifulsoup4`)

## Assumptions

*   Access to OpenAI API keys with sufficient quota for GPT-3.5 and GPT-4o.
*   The initial set of news sources are accessible via RSS or simple web scraping.
*   A single-user context is sufficient for the MVP subscription model.