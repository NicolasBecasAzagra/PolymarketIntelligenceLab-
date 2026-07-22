import logging
import sys
import pandas as pd
import os
import glob
from datetime import datetime
from src.storage.silver import clean_bronze_data
from src.features.builder import FeatureBuilder
from src.ingestion.news_client import NewsClient
from src.features.nlp_sentiment import NLPSentimentAnalyzer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def get_latest_bronze_file(bronze_dir: str = "data/raw") -> str:
    files = glob.glob(os.path.join(bronze_dir, "*.parquet"))
    if not files:
        raise FileNotFoundError(f"No parquet files found in {bronze_dir}")
    # Sort by modification time
    files.sort(key=os.path.getmtime, reverse=True)
    return files[0]

def get_previous_features_file(output_dir: str = "data/processed") -> str:
    files = glob.glob(os.path.join(output_dir, "features_*.parquet"))
    if not files:
        return None
    files.sort(key=os.path.getmtime, reverse=True)
    return files[0]

def main():
    logger.info("Starting Feature Engineering Pipeline...")
    
    try:
        # 1. Find latest Bronze file
        bronze_file = get_latest_bronze_file()
        logger.info(f"Using latest Bronze file: {bronze_file}")

        # 2. Bronze -> Silver (Cleaning)
        silver_df = clean_bronze_data(bronze_file)
        
        # 3. Silver -> Gold (Features)
        gold_features_df = FeatureBuilder.build_features(silver_df)
        
        # 3.5 NLP Sentiment
        logger.info("Fetching news dynamically per market for NLP sentiment analysis...")
        nlp = NLPSentimentAnalyzer()
        gold_features_df = nlp.calculate_sentiment(gold_features_df)
        
        # 3.6 Carry forward previous sentiment if no new news
        prev_file = get_previous_features_file()
        if prev_file:
            try:
                prev_df = pd.read_parquet(prev_file)
                if 'news_sentiment_score' in prev_df.columns and 'id' in prev_df.columns:
                    prev_scores = prev_df[['id', 'news_sentiment_score', 'news_volume']].set_index('id')
                    for idx, row in gold_features_df.iterrows():
                        market_id = row['id']
                        if row.get('news_volume', 0) == 0 and market_id in prev_scores.index:
                            gold_features_df.at[idx, 'news_sentiment_score'] = prev_scores.at[market_id, 'news_sentiment_score']
                            gold_features_df.at[idx, 'news_volume'] = prev_scores.at[market_id, 'news_volume']
            except Exception as e:
                logger.warning(f"Could not carry forward previous sentiment: {e}")
        
        # 4. Save to Processed layer
        output_dir = "data/processed"
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp_str = datetime.now().strftime("%Y%m%d_%H")
        filename = f"features_{timestamp_str}.parquet"
        filepath = os.path.join(output_dir, filename)
        
        # Convert all columns to string if they are complex (failsafe for PyArrow)
        for col in gold_features_df.columns:
            if gold_features_df[col].dtype == 'object':
                gold_features_df[col] = gold_features_df[col].astype(str)

        gold_features_df.to_parquet(filepath, engine="pyarrow", index=False)
        logger.info(f"Feature engineering successful. Saved to {filepath}")

    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
