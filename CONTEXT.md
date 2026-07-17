# Polymarket Intelligence Lab

**Positioning:** An end-to-end research and intelligence platform for prediction markets, combining data pipelines, multimodal ML, explainable forecasting, and opportunity ranking.

## 🎯 Core Vision
Una plataforma end-to-end que ingiere datos de mercado, order book y contexto textual, construye features multi-horizonte, entrena varios modelos, detecta anomalías, rankea oportunidades, genera explicaciones automáticas y evalúa estrategias con backtesting reproducible.

Combina Data Engineering, Machine Learning, LLMs, Backend/API, Dashboard, evaluación científica y opcionalmente ejecución simulada o paper trading.

## ✨ Lo que lo hace especial (Diferenciadores)
La innovación no es "usar ChatGPT para resumir mercados". Es combinar **señales estructuradas + texto + explicabilidad + evaluación rigurosa**. 
- Demostrar una arquitectura comparativa real.
- Integrar series temporales, texto y razonamiento explicable.
- Reconocer que distintos modelos funcionan mejor según el contexto y la volatilidad.

### Arquitectura Comparativa
1. **Baselines clásicos:** XGBoost o LightGBM.
2. **Modelos time-series potentes:** N-BEATS, NHITS o PatchTST.
3. **Capa LLM:** Para explicaciones, tagging de eventos o fusión multimodal.
4. **Ensemble final:** Combina señales cuantitativas y contexto textual.

## 🏗️ La Arquitectura Monstruo (8 Capas)

1. **Ingesta**
   - Polymarket markets, order book, trades, liquidity, spreads, snapshots.
   - News/event feeds y (opcionalmente) X/Reddit.
   - Metadata del mercado, categorías, tiempo hasta resolución, cambios bruscos.
2. **Storage**
   - Raw lake en S3 o equivalente.
   - Bronze/Silver/Gold con Parquet + DuckDB/PostgreSQL para servir rápido.
   - Versionado de datasets y splits temporales reproducibles.
3. **Feature Store**
   - Momentum, volatility, depth imbalance, spread dynamics, order flow, volume spikes.
   - Time-to-event features.
   - Cross-market correlations.
   - Event-text embeddings y sentiment/event classification.
4. **Modeling**
   - *Task A:* Movement classification.
   - *Task B:* Anomaly detection.
   - *Task C:* Opportunity ranking.
   - *Task D:* Calibration and confidence scoring.
   - *Task E (opcional):* Resolution probability forecasting.
5. **LLM Layer**
   - Resume cambios del mercado.
   - Explica por qué el modelo rankea una oportunidad.
   - Etiqueta noticias según impacto esperado.
   - Genera research notes automáticas apoyadas en features y señales reales (sin humo).
6. **Research Engine**
   - Experiment tracking con MLflow o Weights & Biases.
   - Benchmarks automáticos.
   - Ablation studies (sin texto, sin book, sin ensemble, etc.).
   - Walk-forward validation estricta.
7. **Serving**
   - FastAPI.
   - Endpoints de top opportunities, anomaly alerts, explanation cards, model confidence, historical diagnostics.
   - Jobs programados y actualización near-real-time.
8. **Frontend/Demo**
   - Dashboard tipo terminal/research desk.
   - Leaderboard de mercados.
   - Explanation panels.
   - Backtest explorer.
   - Métricas en vivo y modo demo grabado.

## 🧠 Core ML Tasks (Núcleo)
1. **Opportunity Ranking:** Ordenar mercados por potencial interés/ineficiencia (muy vendible).
2. **Anomaly Detection:** Detectar cambios raros en spread/volumen/probabilidad (muy técnico y visual).
3. **Movement Classification:** Predecir movimientos significativos en ventanas temporales (fácil de benchmarkear).

**Capas Premium:**
- **Calibration model:** Para que la confianza del modelo sea interpretable.
- **Explainability system:** SHAP + resumen LLM grounded en features.

## 🔬 Papers y Rigor Científico (El "Mini-Lab")
- **Multimodal forecasting** con series + texto.
- **Comparativa entre modelos especializados** para series temporales (TimeGPT, NBEATS, NHITS, PatchTST, KAN).
- **Explicabilidad explícita** para justificar outputs y analizar fallos.

El README debe incluir secciones serias: hipótesis, datasets, protocolo experimental, métricas, limitaciones y conclusiones.

## 🛠️ Stack Realista pero Brutal
- **Core:** Python
- **Data Analytics:** Polars o pandas + DuckDB
- **Data Layer:** Parquet
- **Serving DB:** PostgreSQL
- **Orquestación:** Airflow o Prefect
- **Feature Store (Opcional):** Feast
- **ML Baselines:** scikit-learn + XGBoost/LightGBM
- **Deep Models:** PyTorch + PatchTST/NHITS/N-BEATS
- **Texto/Embeddings:** Sentence transformers o embeddings API
- **Explicabilidad/LLM:** LLM API
- **Tracking:** MLflow / Weights & Biases (W&B)
- **API:** FastAPI
- **Frontend:** Streamlit o Next.js
- **Ops:** Docker + CI/CD + tests

## 📦 Entregables Clave
1. Un repo limpio y modular.
2. Un dashboard funcional.
3. Un README de nivel alto.
4. Un architecture diagram.
5. Un research report corto con resultados.
6. Un vídeo demo de 2–3 minutos.
7. Posts en LinkedIn mostrando avances y hallazgos.
8. *(Opcional)* Landing page del proyecto.

## 🗺️ Roadmap de 1 Mes
- **Semana 1:** Diseñar arquitectura, cerrar fuentes de datos, ingesta robusta, esquema Bronze/Silver/Gold, primer dataset analítico.
- **Semana 2:** Feature engineering, baselines clásicos, anomaly detection, primer ranking heurístico, backtesting inicial.
- **Semana 3:** Modelos avanzados time-series, capa textual/LLM, explainability, ablations y benchmark.
- **Semana 4:** API, Dashboard, Polish, tests, Docker, README, paper corto, vídeo demo, posts.

## 🚫 Lo que NO hacer (Anti-Patterns)
- **NO** hacer un bot de trading fully autonomous (dispersa y mete demasiados riesgos técnicos y narrativos).
- **NO** hacer un proyecto genérico tipo "AI market predictor" (suena a humo).
- La obsesión debe ser: *arquitectura clara, evaluación rigurosa y presentación impecable*.
