import logging
import feedparser
from typing import List, Dict
import pandas as pd

logger = logging.getLogger(__name__)

class NewsClient:
    """
    Fetches news from public RSS feeds to be used for NLP Sentiment Analysis.
    """
    
    RSS_FEEDS = [
        "https://cointelegraph.com/rss", # Crypto
        "https://www.coindesk.com/arc/outboundfeeds/rss/", # Crypto
        "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10000664", # Finance
        "http://feeds.foxnews.com/foxnews/politics" # Politics
    ]

    def fetch_recent_news(self) -> pd.DataFrame:
        """
        Fetches the latest news from the configured RSS feeds.
        Returns a DataFrame containing titles, summaries, and publication dates.
        """
        logger.info(f"Fetching news from {len(self.RSS_FEEDS)} RSS feeds...")
        all_news = []
        
        for url in self.RSS_FEEDS:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries:
                    # Extract date, fallback to now if missing
                    pub_date = getattr(entry, 'published', None)
                    if pub_date:
                        try:
                            parsed_date = pd.to_datetime(pub_date, utc=True)
                        except:
                            parsed_date = pd.Timestamp.utcnow()
                    else:
                        parsed_date = pd.Timestamp.utcnow()

                    all_news.append({
                        "title": entry.get("title", ""),
                        "summary": entry.get("summary", ""),
                        "source": entry.get("link", url),
                        "published_at": parsed_date
                    })
            except Exception as e:
                logger.warning(f"Error fetching RSS feed {url}: {e}")
                
        if not all_news:
            logger.warning("No news fetched from any source.")
            return pd.DataFrame(columns=["title", "summary", "source", "published_at"])
            
        df = pd.DataFrame(all_news)
        
        # Sort by most recent first
        df = df.sort_values(by="published_at", ascending=False).reset_index(drop=True)
        
        # We only care about the last 24 hours of news to avoid processing old data
        now = pd.Timestamp.utcnow()
        recent_mask = df['published_at'] >= (now - pd.Timedelta(hours=24))
        df = df[recent_mask]
        
        logger.info(f"Fetched {len(df)} recent news items.")
        return df
