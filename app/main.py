from fastapi import FastAPI
from .models import NewsArticle, Company, Subscription

app = FastAPI(
    title="MK News Copilot",
    description="B2B sales intelligence application that aggregates and provides access to relevant news events.",
    version="0.1.0"
)

@app.get("/")
async def root():
    return {"message": "Welcome to MK News Copilot API"}
