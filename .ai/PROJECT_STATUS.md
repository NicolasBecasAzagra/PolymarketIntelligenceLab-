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

### Week 3: Institutional Data & NLP (NEXT)
- [ ] Ingesta de Order Book (L2) para Bid/Ask spread y Whale Detection.
- [ ] Módulo NLP (Twitter/News Sentiment) correlacionado con volumen.
- [ ] Refactor del Feature Builder para soportar series temporales profundas y L2.

### Week 4: Beast Mode Models (Deep Learning & MLOps)
- [ ] Modelos avanzados time-series Transformers (PatchTST / N-BEATS).
- [ ] MLOps Loop: Script de re-entrenamiento automático con mercados cerrados (Self-Learning).
- [ ] Backtesting institucional de la estrategia.

### Week 5: Serving & Demo (Deprioritized for now)
- [ ] FastAPI desplegada con endpoints clave (`src/serving`).
- [ ] Dashboard frontend funcional (Next.js).
- [ ] Tests, Docker, y CI/CD polish.

## 📌 Current Focus
- El sistema básico está desplegado en el VPS recolectando datos. Pausa de desarrollo para acumular histórico. A la vuelta: Comenzaremos con la ingesta de Order Book y NLP.
