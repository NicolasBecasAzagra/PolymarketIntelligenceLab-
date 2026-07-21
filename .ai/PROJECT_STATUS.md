# Project Status: Polymarket Intelligence Lab

This file tracks the high-level roadmap and current global state of the project.

## 📅 Roadmap (Beast Mode Update)

### Week 1: Architecture & Ingestion (COMPLETED)
- [x] Diseñar arquitectura de carpetas y repositorios.
- [x] Cerrar fuentes de datos (Polymarket API Gamma).
- [x] Implementar ingesta robusta (`src/ingestion`).
- [x] Esquema Bronze/Silver/Gold (Parquet/DuckDB).
- [x] Primer dataset analítico generado.

### Week 2: Features, Baselines & Ops (COMPLETED)
- [x] Feature engineering (`src/features`).
- [x] Baselines clásicos (XGBoost y Isolation Forest).
- [x] Anomaly detection implementado.
- [x] Primer ranking heurístico de oportunidades.
- [x] Capa textual/LLM integrada con OpenAI (`src/models/llm`).
- [x] Explainability (SHAP + LLM summaries).
- [x] Scripts de despliegue en VPS y automatización CRON 24/7.

### Week 3: Institutional Data & NLP (COMPLETED)
- [x] Ingesta de Order Book (L2) para Bid/Ask spread y Whale Detection.
- [x] Módulo NLP (Twitter/News Sentiment) correlacionado con volumen.
- [x] Refactor del Feature Builder para soportar series temporales profundas y L2.

### Week 4: Beast Mode Models (Deep Learning & MLOps)
- [ ] Modelos avanzados time-series Transformers (PatchTST / N-BEATS). (Skip por el momento, XGBoost rinde al nivel necesario).
- [x] MLOps Loop: Script de re-entrenamiento automático con mercados cerrados (Self-Learning).
- [x] Backtesting institucional de la estrategia.

### Week 5: Serving & Demo (NEXT)
- [ ] FastAPI desplegada con endpoints clave (`src/serving`).
- [ ] Dashboard frontend funcional (Next.js).
- [ ] Tests, Docker, y CI/CD polish.

## 📌 Current Focus
- Data Engineering, AI, NLP, L2 y MLOps completados al 100%. El sistema está vivo en el VPS aprendiendo. Siguiente paso: Levantar el Backend (FastAPI) y la interfaz visual (Dashboard Next.js).
