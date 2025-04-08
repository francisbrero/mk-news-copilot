from .rss import RSSSourceHandler
from .sec import SECFilingsHandler

class TechCrunchHandler(RSSSourceHandler):
    def __init__(self, max_articles: int = 5):
        super().__init__("TechCrunch", "https://techcrunch.com/feed/", max_articles)

class VentureBeatHandler(RSSSourceHandler):
    def __init__(self, max_articles: int = 5):
        super().__init__("VentureBeat", "https://venturebeat.com/feed/", max_articles)

class ContentMarketingInstituteHandler(RSSSourceHandler):
    def __init__(self, max_articles: int = 5):
        super().__init__("Content Marketing Institute", "https://contentmarketinginstitute.com/feed/", max_articles)

class B2BMarketingHandler(RSSSourceHandler):
    def __init__(self, max_articles: int = 5):
        super().__init__("B2B Marketing", "http://feeds.feedburner.com/b2bmarketing/RpFg", max_articles)

class ReutersBusinessHandler(RSSSourceHandler):
    def __init__(self, max_articles: int = 5):
        super().__init__("Reuters Business", "https://www.reuters.com/rss/business", max_articles)

class CNBCBusinessHandler(RSSSourceHandler):
    def __init__(self, max_articles: int = 5):
        super().__init__("CNBC Business", "https://www.cnbc.com/id/10000664/device/rss/rss.html", max_articles) 