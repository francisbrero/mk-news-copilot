from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, HttpUrl

class Company(BaseModel):
    id: str
    name: str
    website: Optional[HttpUrl] = None
    description: Optional[str] = None
    tags: List[str] = []

class NewsArticle(BaseModel):
    id: str
    url: HttpUrl
    title: str
    content: str
    published_at: datetime
    source: str
    summary: Optional[str] = None
    companies: List[str] = []  # List of company IDs
    topics: List[str] = []
    tags: List[str] = []