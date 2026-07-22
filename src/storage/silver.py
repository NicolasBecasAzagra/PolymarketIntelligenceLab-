import logging
import pandas as pd
import json

logger = logging.getLogger(__name__)

def clean_bronze_data(bronze_filepath: str) -> pd.DataFrame:
    """
    Reads a Bronze Parquet file and cleans it into a Silver-level DataFrame.
    """
    logger.info(f"Loading Bronze data from {bronze_filepath}")
    df = pd.read_parquet(bronze_filepath)
    
    # 1. Date Conversions
    date_cols = ['createdAt', 'updatedAt', 'startDate', 'endDate']
    for col in date_cols:
        if col in df.columns:
            # Coerce errors to NaT for missing or malformed dates
            df[col] = pd.to_datetime(df[col], errors='coerce', utc=True)

    # 2. Numeric Conversions
    numeric_cols = [
        'liquidity', 'volume', 'openInterest', 'volume24hr', 
        'volume1wk', 'volume1mo', 'volume1yr', 'commentCount'
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)

    # 3. Handle Nested JSON strings (like 'tags' and 'markets')
    def parse_json_len(val):
        try:
            if pd.isna(val): return 0
            # Ensure it's a string that can be parsed
            if isinstance(val, str):
                val = val.replace("'", '"') # Basic fix for python dict strings if any
                parsed = json.loads(val)
                return len(parsed) if isinstance(parsed, list) else 1
            elif isinstance(val, list):
                return len(val)
            return 0
        except Exception:
            return 0

    if 'tags' in df.columns:
        df['num_tags'] = df['tags'].apply(parse_json_len)
        
    if 'markets' in df.columns:
        df['num_submarkets'] = df['markets'].apply(parse_json_len)
        
    # 4. Filter to Top 50 markets by volume
    if 'volume' in df.columns:
        df = df.sort_values(by='volume', ascending=False).head(50).copy()

    logger.info(f"Silver cleaning complete. Shape: {df.shape}")
    return df
