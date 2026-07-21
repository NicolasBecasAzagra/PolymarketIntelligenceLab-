import logging
import requests
import pandas as pd
import json

logger = logging.getLogger(__name__)

class ResolutionsClient:
    """
    Fetches closed markets from Polymarket to extract Ground Truth
    for MLOps continuous training.
    """
    
    BASE_URL = "https://gamma-api.polymarket.com/events"

    def fetch_closed_events(self, limit: int = 100) -> pd.DataFrame:
        """
        Fetches recently closed events to find out which markets resolved to Yes/No.
        """
        logger.info(f"Fetching {limit} closed events for Ground Truth extraction...")
        params = {
            "closed": "true",
            "limit": limit
        }
        
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=15)
            response.raise_for_status()
            events = response.json()
            
            resolved_markets = []
            
            for event in events:
                for market in event.get('markets', []):
                    # Only take markets that have an outcome price
                    if market.get('closed') and market.get('outcomePrices'):
                        try:
                            prices_str = market.get('outcomePrices')
                            prices = json.loads(prices_str) if isinstance(prices_str, str) else prices_str
                            if prices and len(prices) >= 1:
                                yes_price = float(prices[0])
                                # If the price of Yes token resolved to > 0.5, it won
                                target = 1 if yes_price > 0.5 else 0
                                resolved_markets.append({
                                    "id": market.get("id"),
                                    "question": market.get("question"),
                                    "outcome": target
                                })
                        except Exception as e:
                            logger.debug(f"Failed to parse outcome for market {market.get('id')}: {e}")
            
            df = pd.DataFrame(resolved_markets)
            logger.info(f"Extracted Ground Truth for {len(df)} closed markets.")
            return df
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching closed events: {e}")
            return pd.DataFrame(columns=["id", "question", "outcome"])
