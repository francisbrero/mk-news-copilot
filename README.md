# MK News Copilot

B2B sales intelligence application that aggregates and provides access to relevant news events from various sources.

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and fill in your OpenAI API key
5. Initialize data files:
   ```bash
   mkdir -p data
   echo '[]' > data/news.json
   echo '[]' > data/companies.json
   ```

## Project Structure

```
.
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── data/
│   ├── news.json
│   └── companies.json
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── data_utils.py
│   └── ai_processor.py
└── scripts/
    └── ingest.py
```

## Development

To start the API server in development mode:
```bash
uvicorn app.main:app --reload
```

API documentation will be available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
