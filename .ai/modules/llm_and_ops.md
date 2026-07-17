# Module Status: Explainability, LLM & Operations

## Goal
Integrate SHAP values to explain XGBoost decisions, use OpenAI API to generate Wall Street style analyst notes, and prepare the repository for continuous execution on a Contabo Linux VPS.

## Current Architecture
- **Explainability:** `shap.TreeExplainer` on XGBoost to quantify feature impact.
- **LLM:** `openai` Python SDK (GPT-4o or similar) with a strict system prompt.
- **Ops:** Bash scripts and crontab for headless hourly execution.

## Tasks
- [x] Add `shap` and `openai` to poetry.
- [x] Implement `ResearchGenerator` for LLM notes.
- [x] Implement VPS deployment scripts.

## Technical Context
- The LLM API call is conditional; if `OPENAI_API_KEY` is not present, it will log a warning but not crash the ML pipeline.
- The VPS scripts are tailored for standard Debian/Ubuntu environments.
