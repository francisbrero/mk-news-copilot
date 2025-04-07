from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, HttpUrl

class Company(BaseModel):
    id: str
    name: str
    website: Optional[HttpUrl] = None
    description: Optional[str] = None

class NewsArticle(BaseModel):
    id: str
    url: HttpUrl
    title: str
    content: str
    published_at: datetime
    source: str
    companies: List[str] = []  # List of company IDs
    topics: List[str] = []
    summary: Optional[str] = None

class Subscription(BaseModel):
    user_id: str
    company_ids: List[str] = []
    topics: List[str] = []

class SubscriptionUpdate(BaseModel):
    company_id: Optional[str] = None
    topic: Optional[str] = None
    action: str  # "add" or "remove"
    tags: List[str] = []