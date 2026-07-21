import json
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
        logger.info(f"Extracted {len(events)} events. Fetching L2 Order Books for markets...")
        
        for event in events:
            markets = event.get('markets', [])
            for market in markets:
                clob_token_ids_str = market.get('clobTokenIds')
                if clob_token_ids_str:
                    try:
                        clob_token_ids = json.loads(clob_token_ids_str) if isinstance(clob_token_ids_str, str) else clob_token_ids_str
                        if clob_token_ids and len(clob_token_ids) > 0:
                            token_id = clob_token_ids[0]
                            book = client.fetch_order_book(token_id)
                            market['order_book_bids'] = json.dumps(book.get('bids', []))
                            market['order_book_asks'] = json.dumps(book.get('asks', []))
                        else:
                            market['order_book_bids'] = "[]"
                            market['order_book_asks'] = "[]"
                    except Exception as e:
                        logger.debug(f"Failed to fetch order book for market {market.get('id')}: {e}")
                        market['order_book_bids'] = "[]"
                        market['order_book_asks'] = "[]"
                else:
                    market['order_book_bids'] = "[]"
                    market['order_book_asks'] = "[]"
                    
        logger.info("Order books fetched successfully.")
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
