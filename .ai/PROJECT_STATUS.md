# Project Status: Polymarket Intelligence Lab

This file tracks the high-level roadmap and current global state of the project.

## 📅 Roadmap (1 Month)

### Week 1: Architecture & Ingestion
- [x] Diseñar arquitectura de carpetas y repositorios.
- [ ] Cerrar fuentes de datos (Polymarket API, News).
- [ ] Implementar ingesta robusta (`src/ingestion`).
- [ ] Esquema Bronze/Silver/Gold (Parquet/DuckDB).
- [ ] Primer dataset analítico generado.

### Week 2: Features & Baselines
- [ ] Feature engineering (`src/features`).
- [ ] Baselines clásicos (`src/models/baselines`).
- [ ] Anomaly detection implementado.
- [ ] Primer ranking heurístico de oportunidades.
- [ ] Backtesting inicial funcionando.

### Week 3: Advanced Models & Explainability
- [ ] Modelos avanzados time-series (`src/models/time_series`).
- [ ] Capa textual/LLM integrada (`src/models/llm`).
- [ ] Explainability (SHAP + LLM summaries).
- [ ] Ablation studies y benchmarks completados.

### Week 4: Serving & Demo
- [ ] FastAPI desplegada con endpoints clave (`src/serving`).
- [ ] Dashboard frontend funcional (Next.js).
- [ ] Tests, Docker, y CI/CD polish.
- [ ] README completo, paper corto, vídeo demo.

## 📌 Current Focus
- Inicializando la estructura del proyecto y configurando el gestor de dependencias (Poetry) y el frontend (Next.js).
