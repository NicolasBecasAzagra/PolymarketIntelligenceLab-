from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import glob
import os
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
def get_anomalies():
    """
    Returns markets flagged as anomalies by the Isolation Forest model.
    """
    latest_csv = get_latest_file("data/models", "scored_markets_", ".csv")
    if not latest_csv:
        raise HTTPException(status_code=404, detail="No scored markets found.")
        
    try:
        df = pd.read_csv(latest_csv)
        if 'is_anomaly' in df.columns:
            anomalies = df[df['is_anomaly'] == True]
            return anomalies.fillna(0).to_dict(orient="records")
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/system/health")
def health_check():
    return {"status": "online", "mode": "Beast Mode"}
