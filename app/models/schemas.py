from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, HttpUrl, Field, field_validator
from email.utils import parsedate_to_datetime

class Company(BaseModel):
    id: str
    name: str
    website: Optional[HttpUrl] = None
    description: Optional[str] = None

class CompanyCreate(BaseModel):
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

    @field_validator('published_at', mode='before')
    @classmethod
    def parse_date(cls, v):
        if isinstance(v, datetime):
            return v
        if isinstance(v, str):
            try:
                # Try RFC 2822 format first
                return parsedate_to_datetime(v)
            except:
                try:
                    # Try ISO format
                    return datetime.fromisoformat(v)
                except:
                    raise ValueError(f"Unable to parse date: {v}")
        raise ValueError(f"Invalid date format: {v}")

class Subscription(BaseModel):
    user_id: str
    company_ids: List[str] = []
    topics: List[str] = []

class SubscriptionUpdate(BaseModel):
    company_id: Optional[str] = None
    topic: Optional[str] = None
    action: str  # "add" or "remove"
    tags: List[str] = []