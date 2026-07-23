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
            
        title = str(market_row.iloc[0].get('event_title', market_row.iloc[0].get('title', '')))
        outcome = str(market_row.iloc[0].get('outcome', ''))
        search_text = f"{title} {outcome}"
            
        # Strict Keyword Extraction (catch 2+ chars like US, UK, AI, but block all common words)
        STOP_WORDS = {"is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "do", "does", "did", "will", "would", "shall", "should", "can", "could", "may", "might", "must", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", "with", "about", "against", "between", "into", "through", "during", "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s", "t", "just", "don", "now", "called", "election", "market", "price", "time", "year", "month", "day", "week"}
        words = re.findall(r'\b[A-Za-z0-9]{2,}\b', search_text)
        keywords = [w.lower() for w in words if w.lower() not in STOP_WORDS]
        
        if not keywords:
            return {"status": "success", "data": []}
        
        client = NewsClient()
        query = " ".join(keywords)
        news_df = client.fetch_news_for_query(query)
        
        relevant_news = []
        for _, row in news_df.iterrows():
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
                    if positions[m_id]['trade_direction'] == "BUY NO":
                        positions[m_id]['last_price'] = 1.0 - current_prices[m_id] if current_prices[m_id] > 0 else 0.5
                    else:
                        positions[m_id]['last_price'] = current_prices[m_id]
                    
            # Calculate Portfolio Value
            portfolio_value = balance + sum(pos['shares'] * pos['last_price'] for pos in positions.values())
            portfolio_history.append({"timestamp": timestamp, "value": portfolio_value})
            
            # Trading Logic
            for _, row in df.iterrows():
                m_id = str(row['id'])
                event_title = str(row.get('event_title', row.get('title', 'Unknown')))
                outcome = str(row.get('outcome', ''))
                title = f"{event_title} ({outcome})" if outcome else event_title
                score = row.get('master_score', row.get('opportunity_score', 0))
                score_pct = score if score > 1 else score * 100
                directional = float(row.get('directional_confidence', 50.0))
                price = float(row.get('yes_price', 0))
                no_price = 1.0 - price if price > 0 else 0.5
                if price <= 0:
                    price = 0.5
                
                # Trading requires the market to be "hot" (high master_score)
                if score_pct > 70 and m_id not in positions:
                    # Decide direction based on supervised ML model
                    if directional >= 70:
                        trade_direction = "BUY YES"
                        trade_price = price
                        conf = directional
                    elif directional <= 30:
                        trade_direction = "BUY NO"
                        trade_price = no_price
                        conf = 100.0 - directional
                    else:
                        trade_direction = None
                        
                    if trade_direction:
                        # Dynamic position sizing: $50 to $100 based on confidence
                        amount = 50 + ((conf - 70) / 30.0) * 50
                        amount = min(100.0, max(50.0, amount))
                        
                        if balance >= amount:
                            shares = amount / trade_price
                            balance -= amount
                            positions[m_id] = {
                                "shares": shares, 
                                "title": title, 
                                "trade_direction": trade_direction,
                                "last_price": trade_price, 
                                "buy_price": trade_price,
                                "amount_invested": amount
                            }
                            trades.append({
                                "id": m_id,
                                "timestamp": timestamp,
                                "type": trade_direction,
                                "title": title,
                                "price": trade_price,
                                "shares": shares,
                                "amount": amount,
                                "pnl": 0.0,
                                "status": "OPEN"
                            })
                
                # SELL Rule: Take Profit (+30%) or Stop Loss (-20%)
                elif m_id in positions:
                    pos = positions[m_id]
                    buy_price = pos['buy_price']
                    direction = pos['trade_direction']
                    
                    # Track price depending on what we bought
                    current_trade_price = price if direction == "BUY YES" else no_price
                    
                    if current_trade_price >= buy_price * 1.30 or current_trade_price <= buy_price * 0.80:
                        pnl = (current_trade_price - buy_price) * pos['shares']
                        balance += pos['amount_invested'] + pnl
                        trades.append({
                            "id": m_id,
                            "timestamp": timestamp,
                            "type": "SELL",
                            "title": pos['title'],
                            "price": current_trade_price,
                            "shares": pos['shares'],
                            "amount": pos['amount_invested'] + pnl,
                            "pnl": pnl,
                            "status": "CLOSED"
                        })
                        del positions[m_id]
                    
        # Calculate unrealized PNL for still-open positions
        for trade in trades:
            if trade['status'] == "OPEN" and trade['id'] in positions:
                pos = positions[trade['id']]
                trade['pnl'] = (pos['last_price'] - pos['buy_price']) * pos['shares']
                    
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
