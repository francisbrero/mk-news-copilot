# MK News Copilot

A smart news aggregator and filtering system that uses AI to process, tag, and summarize news articles relevant to specific companies and topics.

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
│   ├── utils/              # Utility functions
│   └── ai/                 # AI processing modules
├── scripts/                # Data ingestion scripts
├── tests/                  # Test files
├── .env                    # Environment variables
└── requirements.txt        # Project dependencies
```

## Usage

1. Start the API server:
```bash
uvicorn app.main:app --reload
```

2. Run the news ingestion script:
```bash
python scripts/ingest.py
```

3. Access the API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

- `GET /news` - Get news articles with filtering options
- `GET /companies` - List all companies
- `POST /subscriptions` - Add a subscription
- `GET /subscriptions` - List user subscriptions
- `DELETE /subscriptions` - Remove a subscription
- `GET /feed` - Get personalized news feed

## Development

1. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

2. Run tests:
```bash
pytest
```

## License

MIT 