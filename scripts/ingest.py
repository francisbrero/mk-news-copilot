import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from typing import Dict, List
from app.ai.ai_processor import tag_article, summarize_article
from app.data_utils import read_json_file, write_json_file
from app.news_sources.sources import (
    TechCrunchHandler,
    VentureBeatHandler,
    ContentMarketingInstituteHandler,
    B2BMarketingHandler,
    ReutersBusinessHandler,
    CNBCBusinessHandler,
    SECFilingsHandler
)

def get_news_sources(max_articles_per_source: int = 5):
    """
    Returns a list of initialized news source handlers
    """
    return [
        TechCrunchHandler(max_articles_per_source),
        VentureBeatHandler(max_articles_per_source),
        ContentMarketingInstituteHandler(max_articles_per_source),
        B2BMarketingHandler(max_articles_per_source),
        ReutersBusinessHandler(max_articles_per_source),
        CNBCBusinessHandler(max_articles_per_source),
        SECFilingsHandler(max_articles_per_source),
    ]

def process_articles():
    """
    Main function to fetch, process, and store articles from all sources.
    """
    # Load existing articles
    existing_articles = read_json_file("news.json")
    existing_urls = {article.get("url") for article in existing_articles}
    
    # Initialize sources
    sources = get_news_sources()
    articles_added = 0
    
    # Process each source
    for source in sources:
        print(f"\nFetching articles from {source.source_name}...")
        new_articles = source.fetch_articles()
        
        # Process each new article
        for article in new_articles:
            if article.url in existing_urls:
                continue
                
            # Convert article to dict for storage
            article_dict = {
                "title": article.title,
                "url": article.url,
                "content": article.content,
                "published_at": article.published_at.isoformat(),
                "source": article.source,
                "companies": [],
                "topics": [],
                "summary": ""
            }
            
            # Enrich with AI processing
            tags = tag_article(f"{article.title}\n\n{article.content}")
            article_dict["companies"] = tags["companies"]
            article_dict["topics"] = tags["topics"]
            article_dict["summary"] = summarize_article(f"{article.title}\n\n{article.content}")
            
            # Add to existing articles
            existing_articles.append(article_dict)
            articles_added += 1
            print(f"Processed article: {article.title}")
    
    # Save updated articles
    write_json_file("news.json", existing_articles)
    print(f"\nSaved {articles_added} new articles")

if __name__ == "__main__":
    process_articles()