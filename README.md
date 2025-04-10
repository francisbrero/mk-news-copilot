# MK News Copilot

B2B sales intelligence application that aggregates and provides access to relevant news events from various sources.

## Features

- Automated news ingestion from multiple sources
- AI-powered article tagging and summarization using GPT models
- Company and topic-based filtering
- User subscription system for personalized news feeds
- RESTful API for accessing news and managing subscriptions

## Tech Stack

- Python 3.11+
- FastAPI for the REST API
- OpenAI GPT-3.5/4 for AI processing
- Local JSON storage
- pytest for testing

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd mk-news-copilot
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root:
```
OPENAI_API_KEY=your_api_key_here
```

5. Initialize the data directory:
```bash
mkdir -p data
touch data/news.json
echo "[]" > data/news.json
```

## Project Structure

```
mk-news-copilot/
├── data/                    # JSON data storage
│   ├── news.json           # News articles
│   ├── companies.json      # Company information
│   └── subscriptions.json  # User subscriptions
├── app/
│   ├── models/             # Pydantic models
│   ├── utils/             # Utility functions
│   ├── ai/                # AI processing modules
│   │   └── ai_processor.py # GPT-based article processing
│   └── main.py           # FastAPI application
├── scripts/
│   └── ingest.py         # News ingestion script
├── tests/                 # Test files
├── .env                   # Environment variables
└── requirements.txt       # Project dependencies
```

## Usage

1. Start the API server:
```bash
uvicorn app.main:app --reload
```

[Swagger UI](http://localhost:8000/docs)
[ReDoc](http://localhost:8000/redoc)

2. Run the news ingestion script (fetches and processes articles with AI):
```bash
python scripts/ingest.py
```

The ingest script will:
- Fetch latest articles from configured sources
- Use GPT-3.5 to identify mentioned companies and topics
- Use GPT-4 to generate concise summaries
- Save processed articles to data/news.json

3. Access the API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### News

- `GET /news`
  - Get news articles with filtering options
  - Query parameters:
    - `company`: Filter by company ID
    - `topic`: Filter by topic
    - `start_date`: Filter by date (ISO format)
    - `end_date`: Filter by date (ISO format)

### Companies

- `GET /companies`
  - List all companies
  - Query parameters:
    - `name`: Filter companies by name (case-insensitive)

### Subscriptions

- `GET /subscriptions`
  - Get user's subscriptions
  - Query parameters:
    - `user_id`: User identifier

- `POST /subscriptions`
  - Add or remove a subscription
  - Query parameters:
    - `user_id`: User identifier
  - Request body:
    ```json
    {
      "company_id": "string",  // optional
      "topic": "string",       // optional
      "action": "add"         // "add" or "remove"
    }
    ```

- `DELETE /subscriptions`
  - Clear all subscriptions for a user
  - Query parameters:
    - `user_id`: User identifier

### Feed

- `GET /feed`
  - Get personalized news feed based on subscriptions
  - Query parameters:
    - `user_id`: User identifier
    - `start_date`: Filter by date (ISO format, optional)
    - `end_date`: Filter by date (ISO format, optional)

## Example Usage

```bash
# Get all news articles
curl http://localhost:8000/news

# Get news for a specific company
curl http://localhost:8000/news?company=company_id

# Get news for a specific topic
curl http://localhost:8000/news?topic=Fundraising

# Get news within a date range
curl "http://localhost:8000/news?start_date=2024-01-01T00:00:00&end_date=2024-12-31T23:59:59"

# Subscribe to a company
curl -X POST "http://localhost:8000/subscriptions?user_id=user1" \
  -H "Content-Type: application/json" \
  -d '{"company_id": "company_id", "action": "add"}'

# Get personalized feed
curl "http://localhost:8000/feed?user_id=user1"
```

## Development

1. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

2. Run tests:
```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=app tests/

# Run specific test file
pytest tests/test_api.py

# Run tests with verbose output
pytest -v
```

3. Code formatting and linting:
```bash
# Format code with black
black app/ tests/

# Sort imports
isort app/ tests/

# Run flake8 linting
flake8 app/ tests/
```

4. Test Structure:
```
tests/
├── test_api.py           # API endpoint tests
├── test_ai_processor.py  # AI processing tests
└── test_data_utils.py    # Data utility tests
```

The test suite includes:
- API endpoint tests with request/response validation
- AI processor tests with mocked OpenAI calls
- Data utility tests for file operations
- Error handling and edge cases
- Mock data fixtures for consistent testing

## License

MIT