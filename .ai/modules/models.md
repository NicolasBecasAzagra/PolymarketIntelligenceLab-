# Module Status: Machine Learning Models (Baselines)

## Goal
Build robust, professional baselines for Opportunity Ranking and Anomaly Detection using cross-sectional market data.

## Current Architecture
- **Anomaly Detection:** `IsolationForest` (unsupervised, scikit-learn).
- **Opportunity Ranking:** `XGBoostRegressor` trained on synthetic opportunity score based on volume and liquidity.
- **Tracking:** `MLflow` logs hyperparameters, metrics, and models.
- **Orchestration:** `src/models/run_models.py` sequentially loads Gold features, applies models, and saves results.

## Tasks
- [x] Isolation Forest Anomaly Detector.
- [x] XGBoost Opportunity Ranker.
- [x] Orchestration script and MLflow integration.

## Technical Context
- We are using a synthetic target for the XGBoost model because we don't have historical resolution data yet.
- The Anomaly Detector flags markets that behave unusually in the vector space defined by volume velocity, liquidity health, and social engagement.
