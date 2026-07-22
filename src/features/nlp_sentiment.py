import logging
import pandas as pd
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

logger = logging.getLogger(__name__)

class NLPSentimentAnalyzer:
    """
    Analyzes market questions against recent news to determine sentiment scores
    using NLTK VADER.
    """
    
    def __init__(self):
        try:
            # Ensure VADER lexicon is downloaded
            nltk.data.find('sentiment/vader_lexicon.zip')
        except LookupError:
            logger.info("Downloading NLTK VADER lexicon...")
            nltk.download('vader_lexicon', quiet=True)
            
        self.analyzer = SentimentIntensityAnalyzer()
        
    def _extract_keywords(self, question: str) -> list:
        """
        Extracts basic keywords from a Polymarket question to search in news.
        Simple implementation: ignores common words, keeps uppercase or long words.
        """
        if not isinstance(question, str):
            return []
            
        words = question.replace('?', '').replace(',', '').split()
        keywords = []
        
        # Stopwords simplificados
        stop_words = {'Will', 'will', 'the', 'in', 'be', 'a', 'to', 'of', 'and', 'for', 'by', 'on', 'is', 'who'}
        
        for w in words:
            if w not in stop_words and len(w) > 3:
                keywords.append(w.lower())
                
        return keywords

    def calculate_sentiment(self, markets_df: pd.DataFrame) -> pd.DataFrame:
        """
        Cross-references markets with dynamic Google News search to calculate sentiment.
        Adds 'news_sentiment_score' and 'news_volume' to the DataFrame.
        """
        import time
        import re
        from src.ingestion.news_client import NewsClient
        
        logger.info("Calculating NLP Sentiment dynamically via Google News...")
        
        sentiment_scores = []
        news_volumes = []
        client = NewsClient()
        query_cache = {}
        
        STOP_WORDS = {"is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "do", "does", "did", "will", "would", "shall", "should", "can", "could", "may", "might", "must", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", "with", "about", "against", "between", "into", "through", "during", "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s", "t", "just", "don", "now", "called", "election", "market", "price", "time", "year", "month", "day", "week"}
        
        for idx, row in markets_df.iterrows():
            title = row.get('event_title', row.get('title', ''))
            outcome = row.get('outcome', '')
            search_text = f"{title} {outcome}"
            
            # very basic keyword extraction
            words = re.findall(r'\b[a-zA-Z]{3,}\b', search_text)
            keywords = [w.lower() for w in words if w.lower() not in STOP_WORDS]
            
            if not keywords:
                sentiment_scores.append(0.0)
                news_volumes.append(0.0)
                continue
                
            query = " ".join(keywords)
            
            # Check Cache first (since multiple markets share the same event question)
            if query in query_cache:
                sentiment_scores.append(query_cache[query]['score'])
                news_volumes.append(query_cache[query]['volume'])
                continue
                
            try:
                news_df = client.fetch_news_for_query(query)
            except Exception as e:
                logger.error(f"Failed to fetch news for {query}: {e}")
                news_df = pd.DataFrame()
            
            if news_df.empty:
                sentiment_scores.append(0.0)
                news_volumes.append(0.0)
                query_cache[query] = {'score': 0.0, 'volume': 0.0}
            else:
                news_df['full_text'] = (news_df['title'].fillna('') + " " + news_df['summary'].fillna('')).str.lower()
                scores = []
                for text in news_df['full_text']:
                    vs = self.analyzer.polarity_scores(text)
                    scores.append(vs['compound'])
                    
                avg_sentiment = sum(scores) / len(scores) if scores else 0.0
                news_volume_val = float(len(scores))
                
                sentiment_scores.append(avg_sentiment)
                news_volumes.append(news_volume_val)
                query_cache[query] = {'score': avg_sentiment, 'volume': news_volume_val}
                
            # Be nice to Google RSS API
            time.sleep(0.5)
                
        markets_df['news_sentiment_score'] = sentiment_scores
        markets_df['news_volume'] = news_volumes
        
        logger.info(f"Sentiment analysis complete. Found relevant news for {sum(v > 0 for v in news_volumes)} markets.")
        return markets_df
