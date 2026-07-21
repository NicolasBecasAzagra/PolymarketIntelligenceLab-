# Module Status: Feature Engineering (Silver & Gold)

## Goal
Transform raw Bronze Parquet files into a clean Silver layer, and then into a Gold layer containing deep ML features (momentum, time-decay, engagement).

## Current Architecture
- **Engine:** Pandas/Polars for heavy lifting.
- **Silver Layer:** Cleans date formats, un-nests JSON arrays (e.g., tags, outcomes), and casts types.
- **Gold Layer (Feature Builder):** 
  - Time-to-event metrics.
  - Volume Momentum (1d vs 1wk vs 1mo).
  - Engagement scores.
  - **L2 Order Book**: Spread, Liquidity Imbalance, Whale Walls.
  - **NLP Sentiment**: VADER sentiment score and news volume from RSS.
- **Storage:** Saved to `data/processed/features_YYYYMMDD_HH.parquet`.

## Tasks
- [x] Silver layer cleaning functions (`src/storage/silver.py`).
- [x] Deep feature extraction (`src/features/builder.py`).
- [x] Orchestration script (`run_features.py`).
- [x] NLP Sentiment Integration (`src/features/nlp_sentiment.py`).
- [x] L2 Orderbook Parsing.

## Technical Context
- The features generated here are fed directly into the XGBoost Opportunity Ranker and the MLOps Supervised Trainer.
