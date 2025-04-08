from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, HttpUrl, EmailStr

class Company(BaseModel):
    name: str
    logo_url: Optional[HttpUrl] = None
    size: Optional[str] = None
    industry: Optional[str] = None
    headquarters: Optional[str] = None

class CompanyCreate(Company):
    pass

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

class SubscriptionUpdate(BaseModel):
    company_id: Optional[str] = None
    topic: Optional[str] = None
    action: Literal["add", "remove"]

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