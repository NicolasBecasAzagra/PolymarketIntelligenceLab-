import logging
import pandas as pd
import os
import time
import re
from openai import OpenAI
from src.ingestion.news_client import NewsClient

logger = logging.getLogger(__name__)

class NLPSentimentAnalyzer:
    """
    Analyzes market questions against recent news to determine sentiment scores
    using OpenAI's gpt-4o-mini LLM.
    """
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not found. Sentiment will default to 0.0.")
            self.client = None
        else:
            self.client = OpenAI(api_key=self.api_key)
            
    def calculate_sentiment(self, markets_df: pd.DataFrame) -> pd.DataFrame:
        """
        Cross-references markets with dynamic Google News search to calculate sentiment.
        Adds 'news_sentiment_score', 'news_volume', and 'top_news_headline' to the DataFrame.
        """
        logger.info("Calculating NLP Sentiment dynamically via OpenAI...")
        
        sentiment_scores = []
        news_volumes = []
        top_headlines = []
        news_client = NewsClient()
        query_cache = {}
        
        STOP_WORDS = {"is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "do", "does", "did", "will", "would", "shall", "should", "can", "could", "may", "might", "must", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", "with", "about", "against", "between", "into", "through", "during", "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s", "t", "just", "don", "now", "called", "election", "market", "price", "time", "year", "month", "day", "week"}
        
        for idx, row in markets_df.iterrows():
            title = row.get('event_title', row.get('title', ''))
            outcome = row.get('outcome', '')
            search_text = f"{title} {outcome}"
            
            words = re.findall(r'\b[a-zA-Z]{3,}\b', search_text)
            keywords = [w.lower() for w in words if w.lower() not in STOP_WORDS]
            
            if not keywords:
                sentiment_scores.append(0.0)
                news_volumes.append(0.0)
                top_headlines.append("")
                continue
                
            query = " ".join(keywords)
            
            if query in query_cache:
                sentiment_scores.append(query_cache[query]['score'])
                news_volumes.append(query_cache[query]['volume'])
                top_headlines.append(query_cache[query]['headline'])
                continue
                
            try:
                news_df = news_client.fetch_news_for_query(query)
            except Exception as e:
                logger.error(f"Failed to fetch news for {query}: {e}")
                news_df = pd.DataFrame()
            
            if news_df.empty:
                sentiment_scores.append(0.0)
                news_volumes.append(0.0)
                top_headlines.append("")
                query_cache[query] = {'score': 0.0, 'volume': 0.0, 'headline': ""}
            else:
                top_headline = str(news_df['title'].iloc[0])
                news_volume_val = float(len(news_df))
                
                if self.client:
                    news_text = "\n".join(news_df['title'].head(5).tolist())
                    prompt = (
                        f"Market: {title}\nOption to Buy: {outcome}\n\nRecent News Headlines:\n{news_text}\n\n"
                        "Evaluate the impact of these headlines on the probability of the Option resolving to YES. "
                        "Rate from -1.0 (strongly bearish/negative) to 1.0 (strongly bullish/positive). Return ONLY a float number."
                    )
                    
                    try:
                        resp = self.client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[{"role": "user", "content": prompt}],
                            temperature=0.0,
                            max_tokens=10
                        )
                        score_str = resp.choices[0].message.content.strip()
                        # Extract float from response if LLM added any extra text
                        match = re.search(r'-?\d+\.\d+', score_str)
                        if match:
                            avg_sentiment = float(match.group())
                        else:
                            # Try just finding digits
                            match = re.search(r'-?\d+', score_str)
                            avg_sentiment = float(match.group()) if match else 0.0
                        # Clamp between -1.0 and 1.0
                        avg_sentiment = max(-1.0, min(1.0, avg_sentiment))
                    except Exception as e:
                        logger.error(f"LLM sentiment failed: {e}")
                        avg_sentiment = 0.0
                else:
                    avg_sentiment = 0.0
                
                sentiment_scores.append(avg_sentiment)
                news_volumes.append(news_volume_val)
                top_headlines.append(top_headline)
                query_cache[query] = {'score': avg_sentiment, 'volume': news_volume_val, 'headline': top_headline}
                
            time.sleep(0.5)
                
        markets_df['news_sentiment_score'] = sentiment_scores
        markets_df['news_volume'] = news_volumes
        markets_df['top_news_headline'] = top_headlines
        
        logger.info(f"Sentiment analysis complete. Found relevant news for {sum(v > 0 for v in news_volumes)} markets.")
        return markets_df
