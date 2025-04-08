import requests
from bs4 import BeautifulSoup
from typing import List
from .base import NewsSourceHandler, Article

class RSSSourceHandler(NewsSourceHandler):
    def fetch_articles(self) -> List[Article]:
        try:
            response = requests.get(self.feed_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, features="xml")
            articles = []
            
            for item in soup.find_all("item")[:self.max_articles]:
                try:
                    article = Article(
                        title=item.title.text,
                        url=item.link.text,
                        content=item.description.text if item.description else "",
                        published_at=self.process_date(item.pubDate.text),
                        source=self.source_name,
                        companies=[],
                        topics=[],
                        summary=""
                    )
                    articles.append(article)
                except Exception as e:
                    print(f"Error processing article from {self.source_name}: {str(e)}")
                    continue
                    
            return articles
        except Exception as e:
            print(f"Error fetching articles from {self.source_name}: {str(e)}")
            return [] 