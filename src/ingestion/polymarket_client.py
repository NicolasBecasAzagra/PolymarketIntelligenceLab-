import logging
import requests
from typing import Dict, Any, List
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)

class PolymarketClient:
    """
    Client to interact with Polymarket APIs.
    We start with the Gamma API to fetch active events and their metadata.
    """
    GAMMA_API_URL = "https://gamma-api.polymarket.com"
    CLOB_API_URL = "https://clob.polymarket.com"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "PolymarketIntelligenceLab/0.1.0"
        })

    def fetch_active_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Fetches a list of active events/markets.
        """
        endpoint = f"{self.GAMMA_API_URL}/events"
        params = {
            "active": "true",
            "closed": "false",
            "limit": limit
        }
        
        logger.info(f"Fetching active events from {endpoint} with params: {params}")
        
        try:
            response = self.session.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data
        except RequestException as e:
            logger.error(f"Error fetching data from Polymarket API: {e}")
            raise

    def fetch_order_book(self, token_id: str) -> Dict[str, Any]:
        """
        Fetches the L2 Order Book (Bids and Asks) for a specific CLOB token ID.
        """
        endpoint = f"{self.CLOB_API_URL}/book"
        params = {"token_id": token_id}
        
        try:
            response = self.session.get(endpoint, params=params, timeout=5)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            logger.debug(f"Could not fetch order book for token {token_id}: {e}")
            # Return an empty structure if it fails (market might be closed or invalid token)
            return {"bids": [], "asks": []}
