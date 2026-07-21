import os
import glob
import logging
import pandas as pd
from src.ingestion.resolutions_client import ResolutionsClient

logger = logging.getLogger(__name__)

class MLOpsDatasetBuilder:
    """
    Combines historical feature parquets with actual Ground Truth (closed markets)
    to build a supervised training dataset.
    """
    def __init__(self, features_dir: str = "data/processed", output_dir: str = "data/mlops"):
        self.features_dir = features_dir
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
    def build_training_dataset(self) -> pd.DataFrame:
        logger.info("Starting MLOps Dataset Builder...")
        
        # 1. Fetch Ground Truth
        client = ResolutionsClient()
        gt_df = client.fetch_closed_events(limit=500)
        
        if gt_df.empty:
            logger.warning("No closed events found. Cannot build dataset.")
            return pd.DataFrame()
            
            
        gt_df['target'] = gt_df['outcome'].astype(int)
        closed_ids = set(gt_df['id'].unique())
        
        # 2. Load Historical Features
        feature_files = glob.glob(os.path.join(self.features_dir, "features_*.parquet"))
        if not feature_files:
            logger.warning("No historical features found.")
            return pd.DataFrame()
            
        logger.info(f"Loading {len(feature_files)} historical feature files...")
        
        all_features = []
        for f in feature_files:
            try:
                df = pd.read_parquet(f)
                # Keep only closed markets to save memory
                if 'id' in df.columns:
                    df = df[df['id'].isin(closed_ids)]
                    if not df.empty:
                        all_features.append(df)
            except Exception as e:
                logger.debug(f"Error reading {f}: {e}")
                
        if not all_features:
            logger.warning("No historical features match the closed markets yet.")
            return pd.DataFrame()
            
        history_df = pd.concat(all_features, ignore_index=True)
        
        # 3. For each market, get the latest features before it closed
        # We assume the most recent timestamp in our history represents its final state
        # (Actually, 'updatedAt' or just drop duplicates keeping last)
        history_df = history_df.drop_duplicates(subset=['id'], keep='last')
        
        # 4. Merge Features with Target
        dataset = pd.merge(history_df, gt_df[['id', 'target']], on='id', how='inner')
        
        output_path = os.path.join(self.output_dir, "training_dataset.parquet")
        
        # Failsafe for Pyarrow
        for col in dataset.columns:
            if dataset[col].dtype == 'object':
                dataset[col] = dataset[col].astype(str)
                
        dataset.to_parquet(output_path, engine='pyarrow', index=False)
        logger.info(f"Successfully built supervised dataset with {len(dataset)} examples. Saved to {output_path}")
        return dataset

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    builder = MLOpsDatasetBuilder()
    builder.build_training_dataset()
