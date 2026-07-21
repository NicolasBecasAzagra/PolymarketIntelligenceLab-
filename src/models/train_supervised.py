import os
import logging
import pandas as pd
import xgboost as xgb
import mlflow
import mlflow.xgboost
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, roc_auc_score

logger = logging.getLogger(__name__)

class SupervisedTrainer:
    """
    Trains an XGBoost Classifier on Ground Truth data and logs it to MLflow.
    """
    def __init__(self, dataset_path: str = "data/mlops/training_dataset.parquet"):
        self.dataset_path = dataset_path
        self.feature_cols = [
            'liquidity', 'volume', 'volume24hr',
            'days_to_resolution', 'urgency_score',
            'velocity_24h', 'velocity_1wk',
            'liquidity_to_oi_ratio', 'comments_per_1k_volume',
            'bid_ask_spread', 'liquidity_imbalance', 'whale_wall_size',
            'news_sentiment_score', 'news_volume'
        ]

    def train_and_log(self):
        logger.info("Starting Supervised Training...")
        
        if not os.path.exists(self.dataset_path):
            logger.error(f"Dataset not found at {self.dataset_path}. Run MLOpsDatasetBuilder first.")
            return
            
        df = pd.read_parquet(self.dataset_path)
        if df.empty or len(df) < 10:
            logger.warning("Dataset is too small for meaningful training.")
            return
            
        # Ensure columns exist and fillna
        available_features = [c for c in self.feature_cols if c in df.columns]
        X = df[available_features].fillna(0.0)
        y = df['target']
        
        # We need both classes to train
        if len(y.unique()) < 2:
            logger.warning("Dataset contains only one class. Cannot train classifier.")
            return
            
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Setup MLflow
        mlflow.set_experiment("Polymarket_MLOps")
        
        with mlflow.start_run():
            model = xgb.XGBClassifier(
                n_estimators=100,
                max_depth=4,
                learning_rate=0.1,
                random_state=42,
                eval_metric="auc"
            )
            
            logger.info("Fitting XGBoost Classifier to Ground Truth data...")
            model.fit(X_train, y_train)
            
            # Evaluate
            preds = model.predict(X_test)
            probs = model.predict_proba(X_test)[:, 1]
            
            acc = accuracy_score(y_test, preds)
            prec = precision_score(y_test, preds, zero_division=0)
            try:
                auc = roc_auc_score(y_test, probs)
            except ValueError:
                auc = 0.5 # Default if AUC fails due to only one class in test set
                
            logger.info(f"Model Metrics -> Accuracy: {acc:.3f}, Precision: {prec:.3f}, AUC: {auc:.3f}")
            
            mlflow.log_metric("accuracy", acc)
            mlflow.log_metric("precision", prec)
            mlflow.log_metric("auc", auc)
            
            # Log the model
            mlflow.xgboost.log_model(
                xgb_model=model,
                artifact_path="model",
                registered_model_name="Polymarket_Supervised_Ranker"
            )
            logger.info("Successfully trained and logged model to MLflow.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    trainer = SupervisedTrainer()
    trainer.train_and_log()
