import logging
import pandas as pd
import numpy as np
import json
logger = logging.getLogger(__name__)

class FeatureBuilder:
    """
    Constructs deep heuristic features from Silver-level market data.
    These features will feed ML pipelines (classification, anomaly detection).
    """

    @staticmethod
    def build_features(df: pd.DataFrame) -> pd.DataFrame:
        logger.info("Building deep features...")
        features = df.copy()

        # Timestamp for relative calculations
        now = pd.Timestamp.utcnow()

        # 1. Time-decay features (Temporal)
        if 'endDate' in features.columns:
            # Days until the market resolves
            features['days_to_resolution'] = (features['endDate'] - now).dt.total_seconds() / 86400.0
            # Replace NaNs with a large number or 0 if missing
            features['days_to_resolution'] = features['days_to_resolution'].fillna(999.0)
            # Add an urgency metric (exponential decay as it gets closer to 0)
            features['urgency_score'] = np.exp(-np.maximum(features['days_to_resolution'], 0) / 7.0) 
            
        if 'createdAt' in features.columns:
            features['market_age_days'] = (now - features['createdAt']).dt.total_seconds() / 86400.0
            features['market_age_days'] = np.maximum(features['market_age_days'].fillna(0.1), 0.1)

        # 2. Volume Momentum / Velocity features
        # Compares short-term volume against long-term averages
        EPSILON = 1e-9
        
        if 'volume24hr' in features.columns and 'volume1wk' in features.columns:
            avg_daily_wk = features['volume1wk'] / 7.0
            features['velocity_24h'] = features['volume24hr'] / (avg_daily_wk + EPSILON)
            
        if 'volume1wk' in features.columns and 'volume1mo' in features.columns:
            avg_wk_mo = features['volume1mo'] / 4.0
            features['velocity_1wk'] = features['volume1wk'] / (avg_wk_mo + EPSILON)

        # 3. Liquidity and Health Imbalances
        if 'liquidity' in features.columns and 'openInterest' in features.columns:
            # High liquidity vs low OI might indicate a fake/manipulated market or very early stage
            features['liquidity_to_oi_ratio'] = features['liquidity'] / (features['openInterest'] + EPSILON)

        # 4. Engagement & Noise metrics
        if 'commentCount' in features.columns and 'volume' in features.columns:
            # Lots of comments but zero volume = noise/meme market. High volume + low comments = institutional/whale.
            features['comments_per_1k_volume'] = (features['commentCount'] * 1000) / (features['volume'] + EPSILON)

        # 5. Order Book L2 Features (Whale Detection & Microstructure)
        def process_order_book(row):
            metrics = {
                'bid_ask_spread': 1.0, 
                'liquidity_imbalance': 0.5, 
                'whale_wall_size': 0.0
            }
            try:
                bids_str = row.get('order_book_bids', "[]")
                asks_str = row.get('order_book_asks', "[]")
                
                bids = json.loads(bids_str) if isinstance(bids_str, str) else bids_str
                asks = json.loads(asks_str) if isinstance(asks_str, str) else asks_str
                
                if not isinstance(bids, list) or not isinstance(asks, list):
                    return pd.Series(metrics)

                # Convert to float
                bids = [{'price': float(b.get('price', 0)), 'size': float(b.get('size', 0))} for b in bids if 'price' in b and 'size' in b]
                asks = [{'price': float(a.get('price', 0)), 'size': float(a.get('size', 0))} for a in asks if 'price' in a and 'size' in a]
                
                bids = sorted(bids, key=lambda x: x['price'], reverse=True) # Highest bid first
                asks = sorted(asks, key=lambda x: x['price']) # Lowest ask first
                
                if bids and asks:
                    best_bid = bids[0]['price']
                    best_ask = asks[0]['price']
                    metrics['bid_ask_spread'] = max(best_ask - best_bid, 0)
                
                # Imbalance: total bid size vs total ask size
                total_bid_size = sum(b['size'] for b in bids)
                total_ask_size = sum(a['size'] for a in asks)
                total_size = total_bid_size + total_ask_size
                if total_size > 0:
                    metrics['liquidity_imbalance'] = total_bid_size / total_size
                    
                # Whale walls: find max single order size
                max_bid = max([b['size'] for b in bids]) if bids else 0
                max_ask = max([a['size'] for a in asks]) if asks else 0
                metrics['whale_wall_size'] = max(max_bid, max_ask)
                
            except Exception as e:
                logger.debug(f"Error parsing order book: {e}")
                
            return pd.Series(metrics)

        if 'order_book_bids' in features.columns and 'order_book_asks' in features.columns:
            logger.info("Extracting L2 Order Book features (Spread, Imbalance, Whale Walls)...")
            l2_features = features.apply(process_order_book, axis=1)
            features = pd.concat([features, l2_features], axis=1)

        # Drop complex types (like raw dicts/lists or datetime) before saving to Parquet for ML
        cols_to_drop = [c for c in features.columns if features[c].dtype == 'object' or features[c].dtype == 'datetime64[ns, UTC]']
        
        # Keep identifying columns like 'id', 'slug', 'title' if they are string (object), but carefully.
        # Actually, let's keep strings for identity but drop complex python objects.
        def is_complex(val):
            return isinstance(val, (list, dict))
            
        for col in features.columns:
            if features[col].dtype == 'object':
                if features[col].apply(is_complex).any():
                    features.drop(columns=[col], inplace=True)

        logger.info(f"Feature building complete. Final shape: {features.shape}")
        return features
