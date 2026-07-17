import logging
import sys
from src.ingestion.polymarket_client import PolymarketClient
from src.storage.bronze import save_to_bronze

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting Polymarket Ingestion Pipeline...")
    
    # 1. Initialize Client
    client = PolymarketClient()
    
    # 2. Extract
    logger.info("Extracting active events from Polymarket Gamma API...")
    try:
        events = client.fetch_active_events(limit=50)
        logger.info(f"Extracted {len(events)} events.")
    except Exception as e:
        logger.error(f"Failed to extract data: {e}")
        sys.exit(1)

    # 3. Load to Bronze
    logger.info("Loading data into Bronze layer (Parquet)...")
    try:
        filepath = save_to_bronze(events)
        logger.info(f"Ingestion completed successfully. File: {filepath}")
    except Exception as e:
        logger.error(f"Failed to save data to Bronze layer: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
