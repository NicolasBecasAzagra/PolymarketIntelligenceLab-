import logging
import pandas as pd
import numpy as np
import xgboost as xgb
import shap

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

    def get_shap_explanations(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates SHAP values for the features to explain the predictions.
        Returns a DataFrame with the SHAP value for each feature.
        """
        logger.info("Calculating SHAP values...")
        available_features = [c for c in self.feature_cols if c in df.columns]
        X = df[available_features].fillna(0.0)
        
        if X.empty:
            return pd.DataFrame()
            
        explainer = shap.TreeExplainer(self.model)
        shap_values = explainer.shap_values(X)
        
        # Create a dataframe of SHAP values with prefix 'shap_'
        shap_df = pd.DataFrame(shap_values, columns=[f"shap_{c}" for c in available_features], index=df.index)
        return shap_df
