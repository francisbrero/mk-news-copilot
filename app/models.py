from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, HttpUrl

class Company(BaseModel):
    name: str
    logo_url: Optional[HttpUrl] = None
    size: Optional[str] = None
    industry: Optional[str] = None
    headquarters: Optional[str] = None

class NewsArticle(BaseModel):
    title: str
    url: HttpUrl
    source: str
    published_date: datetime
    content: str
    summary: Optional[str] = None
    companies: List[str] = []
    topics: List[str] = []

class Subscription(BaseModel):
    user_id: str
    companies: List[str] = []
    topics: List[str] = []
