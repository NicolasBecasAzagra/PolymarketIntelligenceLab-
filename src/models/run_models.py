import os
import sys
import glob
import logging
import pandas as pd
from datetime import datetime
import mlflow
from dotenv import load_dotenv

load_dotenv()

from src.models.baselines.anomaly_detector import MarketAnomalyDetector
from src.models.baselines.opportunity_ranker import OpportunityRanker
from src.models.llm.research_generator import ResearchGenerator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def get_latest_features_file(features_dir: str = "data/processed") -> str:
    files = glob.glob(os.path.join(features_dir, "features_*.parquet"))
    if not files:
        raise FileNotFoundError(f"No feature parquet files found in {features_dir}")
    files.sort(key=os.path.getmtime, reverse=True)
    return files[0]

def main():
    logger.info("Starting ML Baselines Pipeline...")
    
    try:
        # Load Features
        features_file = get_latest_features_file()
        logger.info(f"Loading features from: {features_file}")
        df = pd.read_parquet(features_file)

        # Setup MLflow
        mlflow.set_tracking_uri("sqlite:///mlruns.db")
        mlflow.set_experiment("Polymarket_Baselines")
        
        with mlflow.start_run():
            # 1. Anomaly Detection
            detector = MarketAnomalyDetector(contamination=0.05)
            df = detector.fit_predict(df)
            
            num_anomalies = int(df['is_anomaly'].sum())
            mlflow.log_param("anomaly_contamination", 0.05)
            mlflow.log_metric("num_anomalies_detected", num_anomalies)

            # 2. Opportunity Ranking
            ranker = OpportunityRanker()
            df = ranker.fit_predict(df)
            
            mlflow.log_param("ranker_model", "XGBRegressor")
            mlflow.log_param("ranker_n_estimators", ranker.model.n_estimators)
            
            # 3. Explainability (SHAP)
            shap_df = ranker.get_shap_explanations(df)
            if not shap_df.empty:
                df = pd.concat([df, shap_df], axis=1)
            
            # Sort by master score
            df = df.sort_values(by="master_score", ascending=False)
            
            # 4. Generate Research Notes (LLM)
            logger.info("Generating Research Notes for Top 3 Markets...")
            generator = ResearchGenerator()
            df['research_note'] = "Not generated"
            
            for i in range(min(3, len(df))):
                idx = df.index[i]
                row = df.loc[idx]
                title = row.get('title', 'Unknown Market')
                metrics = {
                    'volume': row.get('volume', 0),
                    'liquidity': row.get('liquidity', 0),
                    'velocity_24h': row.get('velocity_24h', 0)
                }
                shap_vals = {c: row[c] for c in shap_df.columns} if not shap_df.empty else {}
                
                note = generator.generate_note(title, metrics, shap_vals)
                df.at[idx, 'research_note'] = note
            
            # Log top 1 opportunity score as a metric
            top_score = float(df['master_score'].iloc[0]) if not df.empty else 0.0
            mlflow.log_metric("top_opportunity_score", top_score)
            
            # Save results
            output_dir = "data/models"
            os.makedirs(output_dir, exist_ok=True)
            
            timestamp_str = datetime.now().strftime("%Y%m%d_%H")
            filename = f"scored_markets_{timestamp_str}.csv"
            filepath = os.path.join(output_dir, filename)
            
            # Save top 50 (or all if <50) for inspection, selecting readable columns
            display_cols = ['id', 'title', 'event_title', 'yes_price', 'volume', 'liquidity', 'is_anomaly', 'master_score', 'research_note']
            available_cols = [c for c in display_cols if c in df.columns]
            df[available_cols].head(50).to_csv(filepath, index=False)
            
            logger.info(f"Saved scored and ranked markets to {filepath}")
            
            # Log the artifact to MLflow
            mlflow.log_artifact(filepath)

    except Exception as e:
        logger.exception("Pipeline failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
