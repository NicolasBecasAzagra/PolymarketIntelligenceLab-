import logging
import pandas as pd
import numpy as np
import xgboost as xgb
import shap
import mlflow

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
            'liquidity', 'volume', 'volume24hr',
            'days_to_resolution', 'urgency_score',
            'velocity_24h', 'velocity_1wk',
            'liquidity_to_oi_ratio', 'comments_per_1k_volume',
            'bid_ask_spread', 'liquidity_imbalance', 'whale_wall_size',
            'news_sentiment_score', 'news_volume'
        ]
        
        # Try to load Supervised Model from MLflow
        self.supervised_model = None
        try:
            client = mlflow.tracking.MlflowClient()
            versions = client.search_model_versions("name='Polymarket_Supervised_Ranker'")
            if versions:
                latest_version = sorted(versions, key=lambda v: int(v.version), reverse=True)[0]
                model_uri = f"models:/Polymarket_Supervised_Ranker/{latest_version.version}"
                self.supervised_model = mlflow.sklearn.load_model(model_uri)
                logger.info(f"Loaded Supervised Model from MLflow (version {latest_version.version}).")
            else:
                logger.info("No registered model versions found for Polymarket_Supervised_Ranker.")
        except Exception as e:
            logger.error(f"Error loading model from MLflow: {e}")
            logger.info("Using strictly heuristic baseline.")

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
        
        # Predictions (Regressor outputs continuous values)
        preds = self.model.predict(X)
        
        # Normalize heuristic predictions to 0-100 scale
        p_min = preds.min()
        p_max = preds.max()
        if p_max > p_min:
            heuristic_norm = (preds - p_min) / (p_max - p_min) * 100.0
        else:
            heuristic_norm = np.zeros_like(preds)

        df = df.copy()
        df['is_opportunity_heuristic'] = heuristic_norm > 50
        df['heuristic_score'] = heuristic_norm
        
        # Supervised Model Scoring (Directional YES/NO)
        if self.supervised_model is not None:
            try:
                # Classifier outputs probabilities of YES
                sup_probs = self.supervised_model.predict_proba(X)[:, 1]
                df['directional_confidence'] = sup_probs * 100.0 # scale to 0-100
            except Exception as e:
                logger.warning(f"Supervised model scoring failed: {e}")
                df['directional_confidence'] = 50.0
        else:
            df['directional_confidence'] = 50.0
            
        # The master_score keeps tracking the "hotness" (volatility/liquidity anomaly)
        df['master_score'] = df['heuristic_score']
            
        # Final Ranking based on master_score
        df = df.sort_values(by='master_score', ascending=False).reset_index(drop=True)
        df['rank'] = df.index + 1
        
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
