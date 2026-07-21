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

    def calculate_sentiment(self, markets_df: pd.DataFrame, news_df: pd.DataFrame) -> pd.DataFrame:
        """
        Cross-references markets with news to calculate sentiment.
        Adds 'news_sentiment_score' and 'news_volume' to the DataFrame.
        """
        logger.info("Calculating NLP Sentiment...")
        
        if news_df.empty:
            logger.warning("No news available for sentiment analysis.")
            markets_df['news_sentiment_score'] = 0.0
            markets_df['news_volume'] = 0.0
            return markets_df
            
        # Combine title and summary for analysis
        news_df['full_text'] = (news_df['title'].fillna('') + " " + news_df['summary'].fillna('')).str.lower()
        
        sentiment_scores = []
        news_volumes = []
        
        for _, row in markets_df.iterrows():
            question = row.get('question', '')
            keywords = self._extract_keywords(question)
            
            if not keywords:
                sentiment_scores.append(0.0)
                news_volumes.append(0.0)
                continue
                
            # Find news matching ANY of the strong keywords
            # A more robust approach would use TF-IDF or embeddings, but keyword matching is a solid baseline
            matched_news = news_df[news_df['full_text'].apply(lambda text: any(kw in text for kw in keywords))]
            
            if matched_news.empty:
                sentiment_scores.append(0.0)
                news_volumes.append(0.0)
            else:
                # Score the matched news
                scores = []
                for text in matched_news['full_text']:
                    vs = self.analyzer.polarity_scores(text)
                    scores.append(vs['compound']) # Compound is the normalized score -1 to 1
                    
                # Average sentiment of matched news
                avg_sentiment = sum(scores) / len(scores)
                sentiment_scores.append(avg_sentiment)
                news_volumes.append(float(len(scores)))
                
        markets_df['news_sentiment_score'] = sentiment_scores
        markets_df['news_volume'] = news_volumes
        
        logger.info(f"Sentiment analysis complete. Found relevant news for {sum(v > 0 for v in news_volumes)} markets.")
        return markets_df
