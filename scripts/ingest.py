import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import json
from typing import Dict, List
import requests
from bs4 import BeautifulSoup
from app.ai.ai_processor import tag_article, summarize_article
from app.data_utils import read_json_file, write_json_file

def fetch_techcrunch_articles() -> List[Dict]:
    """
    Fetches latest articles from TechCrunch RSS feed.
    """
    try:
        response = requests.get("https://techcrunch.com/feed/")
        soup = BeautifulSoup(response.content, features="xml")
        articles = []
        
        for item in soup.find_all("item")[:5]:  # Limit to 5 articles for MVP
            article = {
                "title": item.title.text,
                "url": item.link.text,
                "content": item.description.text,
                "published_at": item.pubDate.text,
                "source": "TechCrunch",
                "companies": [],
                "topics": [],
                "summary": ""
            }
            articles.append(article)
            
        return articles
    except Exception as e:
        print(f"Error fetching TechCrunch articles: {str(e)}")
        return []

def process_articles():
    """
    Main function to fetch, process, and store articles.
    """
    # Load existing articles
    existing_articles = read_json_file("news.json")
    existing_urls = {article.get("url") for article in existing_articles}
    
    # Fetch new articles
    new_articles = fetch_techcrunch_articles()
    articles_added = 0
    
    # Process each new article
    for article in new_articles:
        if article["url"] in existing_urls:
            continue
            
        # Enrich with AI processing
        tags = tag_article(f"{article['title']}\n\n{article['content']}")
        article["companies"] = tags["companies"]
        article["topics"] = tags["topics"]
        article["summary"] = summarize_article(f"{article['title']}\n\n{article['content']}")
        
        # Add to existing articles
        existing_articles.append(article)
        articles_added += 1
        print(f"Processed article: {article['title']}")
    
    # Save updated articles
    write_json_file("news.json", existing_articles)
    print(f"Saved {articles_added} new articles")

if __name__ == "__main__":
    process_articles()