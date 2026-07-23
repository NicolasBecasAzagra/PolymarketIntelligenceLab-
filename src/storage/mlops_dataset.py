import os
import glob
import logging
import pandas as pd
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class MLOpsDatasetBuilder:
    """
    Combines historical feature parquets to build a supervised training dataset.
    Target Variable: Does the yes_price increase significantly in the next 12-24 hours?
    1 = Bullish (Price went up)
    0 = Bearish (Price went down or flat)
    """
    def __init__(self, features_dir: str = "data/processed", output_dir: str = "data/mlops"):
        self.features_dir = features_dir
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
    def build_training_dataset(self) -> pd.DataFrame:
        logger.info("Starting Intraday MLOps Dataset Builder...")
        
        feature_files = glob.glob(os.path.join(self.features_dir, "features_*.parquet"))
        if not feature_files:
            logger.warning("No historical features found.")
            return pd.DataFrame()
            
        logger.info(f"Loading {len(feature_files)} historical feature files...")
        
        all_features = []
        for f in feature_files:
            try:
                # Extract timestamp from filename: features_YYYYMMDD_HH.parquet
                basename = os.path.basename(f)
                ts_str = basename.replace("features_", "").replace(".parquet", "")
                dt = datetime.strptime(ts_str, "%Y%m%d_%H")
                
                df = pd.read_parquet(f)
                if df.empty:
                    continue
                df['snapshot_time'] = dt
                all_features.append(df)
            except Exception as e:
                logger.debug(f"Error parsing file {f}: {e}")
                
        if not all_features:
            logger.warning("No valid data loaded from feature files.")
            return pd.DataFrame()
            
        history_df = pd.concat(all_features, ignore_index=True)
        
        # Ensure we have the required columns
        if 'id' not in history_df.columns or 'yes_price' not in history_df.columns:
            logger.error("Missing required columns ('id', 'yes_price') in history.")
            return pd.DataFrame()
            
        # Sort chronologically
        history_df = history_df.sort_values(by=['id', 'snapshot_time'])
        
        training_rows = []
        
        logger.info("Calculating Intraday Price Delta Targets...")
        
        # Group by market ID
        for market_id, group in history_df.groupby('id'):
            group = group.sort_values('snapshot_time').reset_index(drop=True)
            
            for i, row in group.iterrows():
                current_time = row['snapshot_time']
                current_price = pd.to_numeric(row.get('yes_price', 0.5), errors='coerce')
                
                if pd.isna(current_price):
                    continue
                
                # Look for the price at least 12 hours in the future
                future_rows = group[group['snapshot_time'] >= current_time + timedelta(hours=12)]
                if not future_rows.empty:
                    # Take the first available reading after 12 hours
                    future_price = pd.to_numeric(future_rows.iloc[0]['yes_price'], errors='coerce')
                    
                    if pd.isna(future_price):
                        continue
                        
                    price_delta = future_price - current_price
                    
                    # Target assignment: 
                    # Did the price go up by more than 1 cent? -> 1 (Bullish)
                    # Did the price go down by more than 1 cent? -> 0 (Bearish)
                    # Ignore tiny movements as noise
                    if abs(price_delta) >= 0.01:
                        target = 1 if price_delta > 0 else 0
                        row_dict = row.to_dict()
                        row_dict['target'] = target
                        training_rows.append(row_dict)
                        
        if not training_rows:
            logger.warning("Not enough time delta data to create targets. Need at least 12 hours of history for a market.")
            return pd.DataFrame()
            
        dataset = pd.DataFrame(training_rows)
        
        output_path = os.path.join(self.output_dir, "training_dataset.parquet")
        
        # Failsafe for Pyarrow
        for col in dataset.columns:
            if dataset[col].dtype == 'object':
                dataset[col] = dataset[col].astype(str)
                
        # Drop the snapshot_time to avoid confusing XGBoost with datetime objects
        if 'snapshot_time' in dataset.columns:
            dataset = dataset.drop(columns=['snapshot_time'])
            
        dataset.to_parquet(output_path, engine='pyarrow', index=False)
        logger.info(f"Successfully built INTRADAY dataset with {len(dataset)} examples. Saved to {output_path}")
        return dataset

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    builder = MLOpsDatasetBuilder()
    builder.build_training_dataset()
