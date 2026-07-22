import logging
import feedparser
from typing import List, Dict
import pandas as pd

logger = logging.getLogger(__name__)

class NewsClient:
    """
    Fetches news from Google News RSS based on specific query strings.
    """
    
    def fetch_news_for_query(self, query: str) -> pd.DataFrame:
        """
        Fetches the latest news from Google News RSS for the given query.
        Returns a DataFrame containing titles, summaries, and publication dates.
        """
        import urllib.parse
        
        if not query or not query.strip():
            logger.warning("Empty query provided to fetch_news_for_query.")
            return pd.DataFrame(columns=["title", "summary", "source", "published_at"])
            
        encoded_query = urllib.parse.quote_plus(query.strip())
        url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
        
        logger.info(f"Fetching Google News for query: {query}")
        all_news = []
        
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
            logger.warning(f"Error fetching Google News for {query}: {e}")
                
        if not all_news:
            logger.warning(f"No news fetched for query: {query}")
            return pd.DataFrame(columns=["title", "summary", "source", "published_at"])
            
        df = pd.DataFrame(all_news)
        
        # Sort by most recent first
        df = df.sort_values(by="published_at", ascending=False).reset_index(drop=True)
        
        # We only care about the last 48 hours of news for tight context
        now = pd.Timestamp.utcnow()
        recent_mask = df['published_at'] >= (now - pd.Timedelta(hours=48))
        df = df[recent_mask]
        
        logger.info(f"Fetched {len(df)} recent news items for {query}.")
        return df
