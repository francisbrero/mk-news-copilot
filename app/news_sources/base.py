from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Article:
    title: str
    url: str
    content: str
    published_at: datetime
    source: str
    companies: List[str] = None
    topics: List[str] = None
    summary: str = ""

class NewsSourceHandler(ABC):
    def __init__(self, source_name: str, feed_url: str, max_articles: int = 5):
        self.source_name = source_name
        self.feed_url = feed_url
        self.max_articles = max_articles

    @abstractmethod
    def fetch_articles(self) -> List[Article]:
        """Fetch articles from the news source"""
        pass

    def process_date(self, date_str: str) -> datetime:
        """Convert various date formats to datetime"""
        # Add common date formats here as needed
        formats = [
            "%a, %d %b %Y %H:%M:%S %z",  # RFC 822 format
            "%Y-%m-%dT%H:%M:%S%z",       # ISO format
            "%Y-%m-%d %H:%M:%S",         # Basic format
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        raise ValueError(f"Unable to parse date: {date_str}") 