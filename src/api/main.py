from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import glob
import os
import re
from src.ingestion.news_client import NewsClient
import json

app = FastAPI(title="Polymarket Intelligence Lab API")

# Allow CORS for Next.js Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_latest_file(directory: str, prefix: str, ext: str) -> str:
    files = glob.glob(os.path.join(directory, f"{prefix}*{ext}"))
    if not files:
        return None
    files.sort(key=os.path.getmtime, reverse=True)
    return files[0]

@app.get("/api/opportunities")
def get_opportunities(limit: int = 50):
    """
    Returns the latest scored markets from the ML models.
    """
    latest_csv = get_latest_file("data/models", "scored_markets_", ".csv")
    if not latest_csv:
        raise HTTPException(status_code=404, detail="No scored markets found yet. Waiting for ML pipeline.")
        
    try:
        df = pd.read_csv(latest_csv)
        # Sort by rank ascending
        if 'rank' in df.columns:
            df = df.sort_values(by='rank', ascending=True)
            
        # Clean NaNs
        df = df.fillna(0)
        
        # Parse JSON fields safely if needed (like tags)
        def parse_json_safely(val):
            try:
                if isinstance(val, str) and val.startswith('['):
                    return json.loads(val.replace("'", '"'))
            except:
                pass
            return val
            
        if 'tags' in df.columns:
            df['tags'] = df['tags'].apply(parse_json_safely)
            
        # Select top N
        top_n = df.head(limit)
        
        return {
            "timestamp": os.path.basename(latest_csv).replace("scored_markets_", "").replace(".csv", ""),
            "count": len(top_n),
            "data": top_n.to_dict(orient="records")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/anomalies")
def get_anomalies(limit: int = 10):
    """Returns top volume/liquidity anomalies."""
    try:
        latest_file = get_latest_file("data/models", "scored_markets_", ".csv")
        df = pd.read_csv(latest_file)
        
        # Filter anomalies
        anomalies = df[df['is_anomaly'] == True]
        
        # Sort by anomaly score or volume
        if 'anomaly_score' in anomalies.columns:
            anomalies = anomalies.sort_values(by='anomaly_score', ascending=False)
        else:
            anomalies = anomalies.sort_values(by='volume', ascending=False)
            
        return {"status": "success", "data": anomalies.head(limit).to_dict(orient="records")}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/market/{market_id}/history")
def get_market_history(market_id: str):
    """Returns historical score and volume data for a specific market."""
    try:
        files = sorted(glob.glob("data/models/scored_markets_*.csv"))
        if not files:
            raise FileNotFoundError("No historical data found.")
            
        history = []
        for f in files:
            # Extract timestamp from filename: scored_markets_YYYYMMDD_HH.csv
            match = re.search(r'scored_markets_(\d{8}_\d{2})\.csv', f)
            timestamp = match.group(1) if match else "Unknown"
            
            df = pd.read_csv(f)
            # Ensure ID is string for comparison
            df['id'] = df['id'].astype(str)
            market_row = df[df['id'] == str(market_id)]
            
            if not market_row.empty:
                row = market_row.iloc[0]
                score = row.get('master_score', row.get('opportunity_score', 0))
                volume = row.get('volume', 0)
                price = row.get('yes_price', 0)
                history.append({
                    "timestamp": timestamp,
                    "score": float(score),
                    "volume": float(volume),
                    "price": float(price)
                })
                
        return {"status": "success", "data": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/market/{market_id}/news")
def get_market_news(market_id: str):
    """Fetches recent news relevant to the market."""
    try:
        # First get the market title to know what to search for
        latest_file = get_latest_file("data/models", "scored_markets_", ".csv")
        df = pd.read_csv(latest_file)
        df['id'] = df['id'].astype(str)
        market_row = df[df['id'] == str(market_id)]
        
        if market_row.empty:
            raise HTTPException(status_code=404, detail="Market not found")
            
        title = market_row.iloc[0].get('question', market_row.iloc[0].get('title', ''))
        
        # Keyword extraction: >4 chars and not in stopwords
        STOP_WORDS = {"will", "that", "this", "with", "from", "your", "have", "time", "called", "when", "what", "where", "who", "which", "election", "market", "price", "there", "their", "about", "would", "could"}
        words = re.findall(r'\b[A-Za-z]{5,}\b', title)
        keywords = [w.lower() for w in words if w.lower() not in STOP_WORDS]
        
        client = NewsClient()
        news_df = client.fetch_recent_news()
        
        relevant_news = []
        for _, row in news_df.iterrows():
            news_text = (str(row['title']) + " " + str(row['summary'])).lower()
            
            # Use regex to match whole words only to avoid substring false positives
            match_found = False
            for kw in keywords:
                if re.search(rf'\b{kw}\b', news_text):
                    match_found = True
                    break
                    
            if not keywords or match_found:
                relevant_news.append({
                    "title": row['title'],
                    "summary": row['summary'],
                    "source": row['source'],
                    "published_at": str(row['published_at'])
                })
                
            if len(relevant_news) >= 5: # Limit to 5 news items
                break
                
        # Fallback removed: if no specific news found, we return empty list so UI shows "No relevant news"
                
        return {"status": "success", "data": relevant_news}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/simulation")
def run_simulation():
    """Runs a backtest simulation over historical predictions."""
    try:
        files = sorted(glob.glob("data/models/scored_markets_*.csv"))
        if not files:
            return {"status": "success", "data": {"history": [], "trades": []}}
            
        balance = 3000.0
        positions = {} # market_id -> {shares, title, last_price}
        portfolio_history = []
        trades = []
        
        for f in files:
            match = re.search(r'scored_markets_(\d{8}_\d{2})\.csv', f)
            timestamp = match.group(1) if match else "Unknown"
            
            df = pd.read_csv(f)
            df['id'] = df['id'].astype(str)
            
            # Update last prices
            current_prices = {}
            for _, row in df.iterrows():
                current_prices[str(row['id'])] = float(row.get('yes_price', 0))
                
            for m_id in positions:
                if m_id in current_prices:
                    positions[m_id]['last_price'] = current_prices[m_id]
                    
            # Calculate Portfolio Value
            portfolio_value = balance + sum(pos['shares'] * pos['last_price'] for pos in positions.values())
            portfolio_history.append({"timestamp": timestamp, "value": portfolio_value})
            
            # Trading Logic
            for _, row in df.iterrows():
                m_id = str(row['id'])
                title = str(row.get('event_title', row.get('title', 'Unknown')))
                score = row.get('master_score', row.get('opportunity_score', 0))
                score_pct = score if score > 1 else score * 100
                price = float(row.get('yes_price', 0))
                
                # Fallback if price is 0 or missing so the simulation doesn't stall
                if price <= 0: 
                    price = 0.5
                
                # BUY Rule
                if score_pct > 80 and m_id not in positions and balance >= 200:
                    shares = 200 / price
                    balance -= 200
                    positions[m_id] = {"shares": shares, "title": title, "last_price": price}
                    trades.append({
                        "timestamp": timestamp,
                        "type": "BUY",
                        "title": title,
                        "price": price,
                        "shares": shares,
                        "amount": 200
                    })
                
                # SELL Rule
                elif score_pct < 50 and m_id in positions:
                    shares = positions[m_id]['shares']
                    revenue = shares * price
                    balance += revenue
                    trades.append({
                        "timestamp": timestamp,
                        "type": "SELL",
                        "title": title,
                        "price": price,
                        "shares": shares,
                        "amount": revenue
                    })
                    del positions[m_id]
                    
        return {
            "status": "success", 
            "data": {
                "history": portfolio_history, 
                "trades": list(reversed(trades)) # newest first
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/system/health")
def health_check():
    return {"status": "online", "mode": "Beast Mode"}
