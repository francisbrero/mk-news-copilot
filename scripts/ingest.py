#!/usr/bin/env python3

"""News ingestion script.

This script will be implemented to fetch news from various sources,
process them through the AI pipeline, and store them in news.json.
"""

import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict
import sys
import os

# Add the project root to Python path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.news import NewsArticle
from app.utils.data_utils import load_json_file, save_json_file

def fetch_techcrunch_articles() -> List[NewsArticle]:
    """Fetch articles from TechCrunch RSS feed."""
    feed_url = "https://techcrunch.com/feed/"
    feed = feedparser.parse(feed_url)
    articles = []

    for entry in feed.entries:
        try:
            # Extract article content
            response = requests.get(entry.link)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the main article content (adjust selectors based on actual HTML structure)
            content_div = soup.select_one('div.article-content')
            content = content_div.get_text(strip=True) if content_div else entry.summary
            
            article = NewsArticle(
                url=entry.link,
                title=entry.title,
                content=content,
                published_at=datetime(*entry.published_parsed[:6]),
                source="TechCrunch"
            )
            articles.append(article)
        except Exception as e:
            print(f"Error processing article {entry.link}: {str(e)}")
            continue
    
    return articles

def is_duplicate(article: NewsArticle, existing_articles: List[Dict]) -> bool:
    """Check if an article already exists in our database."""
    if not existing_articles or not isinstance(existing_articles, dict):
        return False
    existing_items = existing_articles.get('items', [])
    return any(a.get('url') == str(article.url) for a in existing_items)

def main():
    # Load existing articles
    existing_articles = load_json_file('news.json')
    if not isinstance(existing_articles, dict):
        existing_articles = {'items': []}
    
    # Fetch new articles
    print("Fetching articles from TechCrunch...")
    new_articles = fetch_techcrunch_articles()
    
    # Filter out duplicates and add new articles
    articles_to_add = []
    for article in new_articles:
        if not is_duplicate(article, existing_articles):
            articles_to_add.append(article.model_dump())
    
    if articles_to_add:
        existing_articles['items'].extend(articles_to_add)
        save_json_file('news.json', existing_articles)
        print(f"Added {len(articles_to_add)} new articles")
    else:
        print("No new articles found")

if __name__ == '__main__':
    main()
