from datetime import datetime, timezone
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from app.models import (
    Company, CompanyCreate, NewsArticle, 
    Subscription, SubscriptionCreate, SubscriptionUpdate, 
    User, UserCreate, UserUpdate
)
from app.utils.data_utils import (
    get_news, get_companies, get_subscriptions, save_subscriptions,
    add_company, get_user_by_id, get_user_by_email, create_user,
    update_user, delete_user
)
import subprocess
import sys
import uuid

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

@app.get("/subscriptions/{user_id}", response_model=List[Subscription])
async def get_user_subscriptions(user_id: str):
    subscriptions = get_subscriptions()
    user_subs = [s for s in subscriptions if s["user_id"] == user_id]
    return user_subs

@app.post("/subscriptions", response_model=Subscription)
async def add_subscription(subscription: SubscriptionCreate):
    subscriptions = get_subscriptions()
    now = datetime.now(timezone.utc).isoformat()
    new_sub = {
        "id": str(uuid.uuid4()),
        **subscription.model_dump(),
        "created_at": now,
        "updated_at": now
    }
    subscriptions.append(new_sub)
    save_subscriptions(subscriptions)
    return new_sub

@app.delete("/subscriptions/{subscription_id}", response_model=dict)
async def remove_subscription(subscription_id: str):
    subscriptions = get_subscriptions()
    sub_idx = next((i for i, s in enumerate(subscriptions) if s["id"] == subscription_id), None)
    if sub_idx is None:
        raise HTTPException(status_code=404, detail="Subscription not found")
    subscriptions.pop(sub_idx)
    save_subscriptions(subscriptions)
    return {"status": "success"}

@app.delete("/subscriptions", response_model=dict)
async def delete_subscriptions(user_id: str):
    subscriptions = get_subscriptions()
    subscriptions = [s for s in subscriptions if s["user_id"] != user_id]
    save_subscriptions(subscriptions)
    return {"status": "success"}

@app.get("/feed", response_model=List[NewsArticle])
async def get_user_feed(
    user_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    user_subs = await get_user_subscriptions(user_id)
    news = get_news()
    
    filtered_news = []
    for article in news:
        # Check if article matches any company or topic subscription
        if any(sub for sub in user_subs if 
               (any(c in article.get("companies", []) for c in sub["company_ids"]) or
                any(t in article.get("topics", []) for t in sub["topics"]))):
            
            # Apply date filters if provided
            article_date = datetime.fromisoformat(article["published_at"])
            if start_date and article_date < start_date:
                continue
            if end_date and article_date > end_date:
                continue
                
            filtered_news.append(article)
    
    return filtered_news

@app.post("/news/refresh", status_code=202)
async def refresh_news(background_tasks: BackgroundTasks):
    """Trigger news ingestion in the background"""
    def run_ingest():
        subprocess.run([sys.executable, "scripts/ingest.py"], check=True)
    
    background_tasks.add_task(run_ingest)
    return {"message": "News refresh started"}

@app.post("/users", response_model=User)
async def create_new_user(user: UserCreate):
    """Create a new user"""
    try:
        return create_user(user.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str):
    """Get user details"""
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/users/{user_id}", response_model=User)
async def update_user_details(user_id: str, user_update: UserUpdate):
    """Update user details"""
    updated_user = update_user(user_id, user_update.model_dump(exclude_unset=True))
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

@app.delete("/users/{user_id}", status_code=204)
async def delete_user_account(user_id: str):
    """Delete a user and their subscriptions"""
    if not delete_user(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return None
