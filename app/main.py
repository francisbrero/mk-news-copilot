from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from app.models.schemas import Company, CompanyCreate, NewsArticle, Subscription, SubscriptionUpdate
from app.utils.data_utils import (
    get_news, get_companies, get_subscriptions, save_subscriptions,
    add_company
)

app = FastAPI(
    title="MK News Copilot",
    description="B2B sales intelligence application that aggregates and provides access to relevant news events",
    version="1.0.0"
)

@app.get("/news", response_model=List[NewsArticle])
async def get_news_articles(
    company: Optional[str] = None,
    topic: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    news = get_news()
    
    filtered_news = news
    if company:
        filtered_news = [n for n in filtered_news if company in n.get("companies", [])]
    if topic:
        filtered_news = [n for n in filtered_news if topic in n.get("topics", [])]
    if start_date:
        filtered_news = [n for n in filtered_news if datetime.fromisoformat(n["published_at"]) >= start_date]
    if end_date:
        filtered_news = [n for n in filtered_news if datetime.fromisoformat(n["published_at"]) <= end_date]
    
    return filtered_news

@app.get("/companies", response_model=List[Company])
async def list_companies(name: Optional[str] = None):
    companies = get_companies()
    if name:
        companies = [c for c in companies if name.lower() in c["name"].lower()]
    return companies

@app.post("/companies", response_model=Company)
async def create_company(company: CompanyCreate):
    """Create a new company. Only name is required, website and description are optional."""
    return add_company(company.model_dump())

@app.get("/subscriptions", response_model=Subscription)
async def get_user_subscriptions(user_id: str):
    subscriptions = get_subscriptions()
    user_sub = next((s for s in subscriptions if s["user_id"] == user_id), None)
    if not user_sub:
        return {"user_id": user_id, "company_ids": [], "topics": []}
    return user_sub

@app.post("/subscriptions", response_model=Subscription)
async def update_subscription(user_id: str, update: SubscriptionUpdate):
    subscriptions = get_subscriptions()
    user_sub = next((s for s in subscriptions if s["user_id"] == user_id), None)
    
    if not user_sub:
        user_sub = {"user_id": user_id, "company_ids": [], "topics": []}
        subscriptions.append(user_sub)
    
    if update.company_id:
        if update.action == "add" and update.company_id not in user_sub["company_ids"]:
            user_sub["company_ids"].append(update.company_id)
        elif update.action == "remove" and update.company_id in user_sub["company_ids"]:
            user_sub["company_ids"].remove(update.company_id)
    
    if update.topic:
        if update.action == "add" and update.topic not in user_sub["topics"]:
            user_sub["topics"].append(update.topic)
        elif update.action == "remove" and update.topic in user_sub["topics"]:
            user_sub["topics"].remove(update.topic)
    
    save_subscriptions(subscriptions)
    return user_sub

@app.delete("/subscriptions", response_model=Subscription)
async def clear_subscriptions(user_id: str):
    subscriptions = get_subscriptions()
    user_sub_idx = next((i for i, s in enumerate(subscriptions) if s["user_id"] == user_id), None)
    
    if user_sub_idx is not None:
        subscriptions.pop(user_sub_idx)
        save_subscriptions(subscriptions)
    
    return {"user_id": user_id, "company_ids": [], "topics": []}

@app.get("/feed", response_model=List[NewsArticle])
async def get_user_feed(
    user_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    user_sub = await get_user_subscriptions(user_id)
    news = get_news()
    
    filtered_news = []
    for article in news:
        # Check if article matches any company or topic subscription
        if (any(c in article.get("companies", []) for c in user_sub["company_ids"]) or
            any(t in article.get("topics", []) for t in user_sub["topics"])):
            
            # Apply date filters if provided
            article_date = datetime.fromisoformat(article["published_at"])
            if start_date and article_date < start_date:
                continue
            if end_date and article_date > end_date:
                continue
                
            filtered_news.append(article)
    
    return filtered_news
