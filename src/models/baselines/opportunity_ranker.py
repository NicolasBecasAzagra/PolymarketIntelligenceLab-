import logging
import pandas as pd
import numpy as np
import xgboost as xgb

logger = logging.getLogger(__name__)

class OpportunityRanker:
    """
    Baseline model to score and rank markets.
    Uses a synthetic target based on volume, liquidity, and urgency for this iteration.
    """
    def __init__(self):
        self.model = xgb.XGBRegressor(
            n_estimators=50,
            learning_rate=0.1,
            max_depth=4,
            random_state=42
        )
        self.feature_cols = [
            'velocity_24h', 'velocity_1wk', 'liquidity_to_oi_ratio', 
            'urgency_score', 'market_age_days'
        ]

    def _synthesize_target(self, df: pd.DataFrame) -> pd.Series:
        # A heuristic proxy for 'good opportunity'
        vol = df.get('volume', pd.Series(np.zeros(len(df))))
        liq = df.get('liquidity', pd.Series(np.zeros(len(df))))
        urgency = df.get('urgency_score', pd.Series(np.zeros(len(df))))
        
        target = np.log1p(vol) * 0.4 + np.log1p(liq) * 0.4 + urgency * 10
        return target

    def fit_predict(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info(f"Running XGBoost Opportunity Ranker on {len(df)} markets...")
        
        available_features = [c for c in self.feature_cols if c in df.columns]
        X = df[available_features].fillna(0.0)
        y = self._synthesize_target(df)
        
        if X.empty:
            logger.warning("No valid features found for XGBoost.")
            df['opportunity_score'] = 0.0
            return df
            
        # Fit the regressor
        self.model.fit(X, y)
        
        # Predict the score
        scores = self.model.predict(X)
        
        df = df.copy()
        df['opportunity_score'] = scores
        
        return df
