import logging
import pandas as pd
from sklearn.ensemble import IsolationForest

logger = logging.getLogger(__name__)

class MarketAnomalyDetector:
    """
    Unsupervised model to detect anomalous market states using Isolation Forest.
    Focuses on volume velocity and liquidity imbalances.
    """
    def __init__(self, contamination: float = 0.05):
        self.model = IsolationForest(
            n_estimators=100, 
            contamination=contamination, 
            random_state=42
        )
        self.feature_cols = [
            'velocity_24h', 'velocity_1wk', 
            'liquidity_to_oi_ratio', 'comments_per_1k_volume'
        ]

    def fit_predict(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info(f"Running Isolation Forest Anomaly Detection on {len(df)} markets...")
        
        # Ensure columns exist, fill missing with 0 for robustness
        available_features = [c for c in self.feature_cols if c in df.columns]
        X = df[available_features].fillna(0.0)
        
        if X.empty:
            logger.warning("No valid features found for Anomaly Detection.")
            df['is_anomaly'] = False
            df['anomaly_score'] = 0.0
            return df
            
        # Predictions: -1 for anomaly, 1 for normal
        preds = self.model.fit_predict(X)
        # Decision function: lower values indicate higher abnormality
        scores = self.model.decision_function(X)
        
        # Format output
        df = df.copy()
        df['is_anomaly'] = preds == -1
        df['anomaly_score'] = scores
        
        num_anomalies = df['is_anomaly'].sum()
        logger.info(f"Detected {num_anomalies} anomalies.")
        return df
