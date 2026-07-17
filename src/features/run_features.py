import logging
import sys
import os
import glob
from datetime import datetime
from src.storage.silver import clean_bronze_data
from src.features.builder import FeatureBuilder

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
