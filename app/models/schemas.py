from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, HttpUrl, EmailStr

class Company(BaseModel):
    id: str
    name: str
    domain: str
    logo_url: Optional[HttpUrl] = None
    size: Optional[str] = None
    industry: Optional[str] = None
    headquarters: Optional[str] = None

class CompanyCreate(BaseModel):
    name: str
    domain: str
    logo_url: Optional[HttpUrl] = None
    size: Optional[str] = None
    industry: Optional[str] = None
    headquarters: Optional[str] = None

class NewsArticle(BaseModel):
    id: str
    title: str
    url: HttpUrl
    source: str
    published_at: datetime
    content: str
    summary: Optional[str] = None
    companies: List[str] = []
    topics: List[str] = []

class Subscription(BaseModel):
    id: str
    user_id: str
    company_ids: List[str] = []
    topics: List[str] = []
    created_at: datetime
    updated_at: datetime

class SubscriptionCreate(BaseModel):
    user_id: str
    company_ids: List[str] = []
    topics: List[str] = []

class UserBase(BaseModel):
    email: EmailStr
    name: str
    company: Optional[str] = None
    role: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class User(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime

class SubscriptionUpdate(BaseModel):
    company_id: Optional[str] = None
    topic: Optional[str] = None
    action: Literal["add", "remove"]
