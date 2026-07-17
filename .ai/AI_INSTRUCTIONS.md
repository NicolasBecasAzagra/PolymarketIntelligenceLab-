# AI INSTRUCTIONS: Polymarket Intelligence Lab

This file contains the strict rules for ANY AI assistant working on this repository. 
**CRITICAL: You must read this file and follow these rules in every session.**

## 1. Context Retention Rules
- Before starting any task, **read** `.ai/PROJECT_STATUS.md` to understand the current global state of the project.
- Before working on a specific module (e.g., ingestion, modeling), **read** the corresponding module status file in `.ai/modules/` (e.g., `.ai/modules/ingestion.md`).
- **NEVER finish a task without updating the corresponding status files.** If you complete a feature, move it from TODO/WIP to DONE in the module file, and update any relevant technical context.

## 2. Technical Guidelines
- **Python Code:** Use `Poetry` for dependency management (`pyproject.toml`). All code goes into `src/`.
- **Data Engineering:** Use `duckdb` and `polars`/`pandas` for local processing. Data is stored in `Parquet` format in the Bronze/Silver/Gold architecture.
- **Machine Learning:** 
  - Log all experiments using `MLflow` or `W&B`.
  - Use `scikit-learn` for baselines, `PyTorch` for deep models.
- **Frontend:** Built with Next.js (React).
- **Backend:** Built with FastAPI.

## 3. Gitflow and Operations
- **Branching:** Features should be developed in `feature/name-of-feature` branches. Bugfixes in `bugfix/name`.
- **Commits:** Write clear and concise commit messages.
- Always check if tests pass before recommending a commit. Use `Makefile` commands to test and lint.

## 4. End of Turn Action
- Conclude your turn by explicitly stating which `.ai` tracking files you have updated.
