# Module Status: Machine Learning Models (Baselines)

## Goal
Build robust, professional baselines for Opportunity Ranking and Anomaly Detection using cross-sectional market data.

## Current Architecture
- **Baselines:** 
  - `IsolationForest` (Anomaly Detection) flags volume/liquidity anomalies.
  - `XGBoost` (Opportunity Ranker) scores markets based on heuristics and L2/NLP data.
- **Deep Learning / Advanced:** (Scheduled for Week 4) Time-Series models like PatchTST.
- **Explainability:** SHAP values calculate feature importance for every market score.
- **Tracking:** `MLflow` logs hyperparameters, metrics, and models.
- **Orchestration:** `src/models/run_models.py` sequentially loads Gold features, applies models, and saves results.

## Tasks
- [x] Create generic anomaly detection (`anomaly_detector.py`).
- [x] Create opportunity ranking heuristic (`opportunity_ranker.py`).
- [x] Add SHAP integration.
- [ ] Time-series implementation (Deep Learning).

## Technical Context
- We are using a synthetic target for the XGBoost model because we don't have historical resolution data yet.
- The Anomaly Detector flags markets that behave unusually in the vector space defined by volume velocity, liquidity health, and social engagement.
