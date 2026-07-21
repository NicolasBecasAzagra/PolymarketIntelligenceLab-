# 🔮 Polymarket Intelligence Lab

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![XGBoost](https://img.shields.io/badge/ML-XGBoost-orange.svg)
![MLflow](https://img.shields.io/badge/MLOps-MLflow-blue.svg)

**Polymarket Intelligence Lab** is an institutional-grade, fully automated AI engine designed to extract, analyze, and predict opportunities in [Polymarket](https://polymarket.com/) (the world's largest decentralized prediction market).

Built for quantitative analysis, this engine goes beyond simple volume tracking. It peeks into the **L2 Order Books** to hunt whales, analyzes **live news sentiment** using NLP, and employs an **MLOps Self-Learning Loop** to continuously train itself on closed markets.

---

## 🚀 Key Features

### 1. 🐋 Beast Mode: L2 Order Book & Whale Detection
Unlike basic bots that only look at trading volume, this engine connects directly to the **CLOB (Central Limit Order Book)** API. It calculates:
- **Bid/Ask Spread Imbalances**: Detects hidden buying/selling pressure.
- **Whale Wall Detection**: Scans the market depth for colossal, hidden limit orders (Spoofing/Iceberg detection).

### 2. 📰 NLP News Sentiment (VADER)
Integrated with public RSS feeds (Bloomberg, CoinDesk, Politico), the system features "eyes" to read the news.
- Performs **Keyword Matching** against live markets.
- Uses **NLTK VADER** (Valence Aware Dictionary and sEntiment Reasoner) to calculate a sentiment score from -1.0 (Panic) to +1.0 (Euphoria).
- Differentiates organic volume spikes (backed by real news) from artificial spam.

### 3. 🤖 AI & Machine Learning Pipeline
- **Isolation Forest (Anomaly Detection)**: Unsupervised learning to flag highly anomalous market behavior.
- **XGBoost Opportunity Ranker**: A powerful gradient boosting algorithm that scores markets from 0 to 1 based on time-decay, velocity, liquidity, and sentiment.

### 4. 🔄 MLOps Self-Learning Loop
The true magic of the engine. Every night at 03:00 AM, the system:
1. Connects to Polymarket to fetch the day's **Closed Markets** (Ground Truth).
2. Merges this reality with its historical Parquet features.
3. **Re-trains** its Supervised XGBoost model automatically.
4. Logs the new "brain" to **MLflow**.
The system continuously learns from its mistakes and adapts to new market meta without human intervention.

---

## 🛠 Tech Stack

- **Data Engineering**: Python, Pandas, PyArrow (Parquet Data Lake).
- **Machine Learning**: Scikit-Learn, XGBoost, SHAP.
- **NLP**: NLTK (VADER), Feedparser.
- **MLOps**: MLflow.
- **Package Management**: Poetry.

---

## ⚙️ How to Deploy (Auto-Pilot VPS)

This project is designed to be deployed on a Linux VPS (e.g., Ubuntu on Contabo, DigitalOcean, AWS) and run 24/7 autonomously via Cron jobs.

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/PolymarketIntelligenceLab-.git
cd PolymarketIntelligenceLab-
```

### 2. Install Dependencies (Poetry)
Make sure you have `python3` and `curl` installed.
```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Install Project Dependencies
~/.local/bin/poetry install
```

### 3. Setup the Cron Jobs (Automation)
The engine runs silently in the background. Open your crontab:
```bash
crontab -e
```
Add the following lines to automate the Ingestion, Feature Engineering, Models, and the Nightly MLOps Loop:

```text
# 1. Hourly Data Ingestion (Top 50 + L2 Order Books)
0 * * * * cd /home/YOUR_USER/PolymarketIntelligenceLab- && ~/.local/bin/poetry run python -m src.ingestion.run_ingestion >> /tmp/polymarket_ingestion.log 2>&1

# 2. Hourly Feature Engineering & NLP Sentiment
5 * * * * cd /home/YOUR_USER/PolymarketIntelligenceLab- && ~/.local/bin/poetry run python -m src.features.run_features >> /tmp/polymarket_features.log 2>&1

# 3. Hourly AI Inference & ML Ranking
10 * * * * cd /home/YOUR_USER/PolymarketIntelligenceLab- && ~/.local/bin/poetry run python -m src.models.run_models >> /tmp/polymarket_models.log 2>&1

# 4. Nightly MLOps Self-Learning Loop (03:00 AM)
0 3 * * * cd /home/YOUR_USER/PolymarketIntelligenceLab- && ./scripts/run_mlops.sh >> /tmp/polymarket_mlops.log 2>&1
```

### 4. (Optional) OpenAI Integration
To generate Wall Street-style research notes explaining the AI's decisions, create a `.env` file in the root directory and add your API key:
```env
OPENAI_API_KEY="sk-tu-clave-aqui"
```

---

## 📊 Where is the data?
Everything the engine generates is stored locally and securely in your server:
- **Raw Data (Bronze)**: `data/raw/`
- **Features (Silver/Gold)**: `data/processed/`
- **AI Ranks & Outputs**: `data/models/`
- **MLflow Registry**: `mlruns/`

## 🤝 Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## 📝 License
[MIT](https://choosealicense.com/licenses/mit/)