# Module Status: Explainability, LLM & Operations

## Goal
Integrate SHAP values to explain XGBoost decisions, use OpenAI API to generate Wall Street style analyst notes, and prepare the repository for continuous execution on a Contabo Linux VPS.

## Current Architecture
- **Explainability:** `shap.TreeExplainer` on XGBoost to quantify feature impact.
- **LLM Context Generator:** Uses OpenAI (GPT-4o) to write "Wall Street" style research notes based purely on mathematical SHAP values from the XGBoost model.
- **Deployment & MLOps:** 
  - Scripts for Contabo VPS auto-deployment and CRON scheduling.
  - **Self-Learning Loop:** Nightly cron job fetches closed Ground Truth markets, merges with historical features, re-trains the XGBoost model on real outcomes, and registers it in MLflow (`Polymarket_Supervised_Ranker`).
- **Explainability:** Bridges the gap between numerical `opportunity_score` and human-readable conviction.

## Tasks
- [x] Add `shap` and `openai` to poetry.
- [x] Implement `ResearchGenerator` for LLM notes.
- [x] Implement VPS deployment scripts.
- [x] Implement MLOps Dataset Builder and Supervised Trainer.

## Technical Context
- The LLM API call is conditional; if `OPENAI_API_KEY` is not present, it will log a warning but not crash the ML pipeline.
- The VPS scripts are tailored for standard Debian/Ubuntu environments.
