import os
import logging
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def save_to_bronze(data: List[Dict[str, Any]], layer_path: str = "data/raw") -> str:
    """
    Saves raw API data to the Bronze layer in Parquet format.
    Partitioned by hour to capture intraday volatility.
    """
    if not data:
        logger.warning("No data provided to save_to_bronze.")
        return ""

    # Ensure the directory exists
    os.makedirs(layer_path, exist_ok=True)

    # Generate an hourly timestamp for the filename
    now = datetime.now()
    timestamp_str = now.strftime("%Y%m%d_%H")
    filename = f"markets_{timestamp_str}.parquet"
    filepath = os.path.join(layer_path, filename)

    # Convert to pandas DataFrame and save as Parquet
    df = pd.DataFrame(data)
    
    # We might have nested structures in 'data', so we ensure everything is serializable
    # For bronze layer, it's acceptable to keep columns as object/string if they are dicts
    # Parquet requires string conversion for deeply nested heterogeneous dicts in pandas
    for col in df.columns:
        if df[col].apply(lambda x: isinstance(x, (dict, list))).any():
            df[col] = df[col].astype(str)

    df.to_parquet(filepath, engine="pyarrow", index=False)
    
    logger.info(f"Successfully saved {len(df)} records to Bronze layer: {filepath}")
    return filepath
