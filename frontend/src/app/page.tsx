"use client";

import { useEffect, useState } from "react";
import MarketModal from "../components/MarketModal";

interface Opportunity {
  id: string;
  question?: string;
  title?: string;
  event_title?: string;
  outcome?: string;
  yes_price?: number;
  volume: number;
  liquidity: number;
  master_score?: number;
  directional_confidence?: number;
  opportunity_score?: number;
  rank?: number;
  news_sentiment_score?: number;
  bid_ask_spread?: number;
  liquidity_imbalance?: number;
  llm_analysis?: string;
  research_note?: string;
  tags?: string[];
}

export default function Dashboard() {
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedMarket, setSelectedMarket] = useState<Opportunity | null>(null);

  useEffect(() => {
    // Fetch all opportunities through Next.js proxy
    fetch(`/api/opportunities?limit=1000&t=${Date.now()}`)
      .then((res) => {
        if (!res.ok) throw new Error("Failed to fetch data from API");
        return res.json();
      })
      .then((data) => {
        if (Array.isArray(data.data)) {
          // Explicitly sort by master_score or opportunity_score descending
          const sorted = data.data.sort((a: any, b: any) => {
            const scoreA = a.master_score ?? a.opportunity_score ?? 0;
            const scoreB = b.master_score ?? b.opportunity_score ?? 0;
            return scoreB - scoreA;
          });
          setOpportunities(sorted);
        } else {
          setError("Failed to load opportunities.");
        }
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  const formatMoney = (val: number) => {
    if (!val) return "$0";
    if (val > 1000000) return `$${(val / 1000000).toFixed(1)}M`;
    if (val > 1000) return `$${(val / 1000).toFixed(1)}k`;
    return `$${val.toFixed(0)}`;
  };

  if (loading) return <div className="loader">Connecting to Polymarket Intelligence Lab...</div>;
  if (error) return <div className="loader" style={{color: 'var(--accent-rose)'}}>Error: {error}</div>;

  return (
    <div className="container">
      <header className="header">
        <h1>Polymarket Intelligence Lab</h1>
        <p>Institutional Grade Prediction Market Terminal • {opportunities.length} Markets Tracked</p>
      </header>

      <main className="grid">
        {opportunities.map((opp, idx) => {
          // Calculate L2 bars based on imbalance (-1.0 to 1.0)
          const imb = opp.liquidity_imbalance || 0;
          const bidPct = ((imb + 1) / 2) * 100;
          const askPct = 100 - bidPct;

          // Prioritize event title (which has ...) and render the outcome separately
          const displayTitle = opp.event_title || opp.title || opp.question || "Market Name Unknown";
          const displayRank = opp.rank || idx + 1;
          const displayScore = opp.master_score ?? opp.opportunity_score ?? 0;
          const displayNote = opp.llm_analysis || opp.research_note || "";

          return (
            <div 
              key={opp.id} 
              className="card"
              style={{ animationDelay: `${idx * 0.05}s` }}
              onClick={() => setSelectedMarket(opp)}
            >
              <div className="card-header">
                <span className="card-rank">#{displayRank}</span>
                <h2 className="card-title">
                  {displayTitle}
                  {opp.outcome && (
                    <span style={{ 
                      color: 'var(--accent-green)', 
                      marginLeft: '0.5rem', 
                      background: 'rgba(16,185,129,0.1)', 
                      padding: '2px 8px', 
                      borderRadius: '4px',
                      fontSize: '0.9rem',
                      display: 'inline-block'
                    }}>
                      Option: {opp.outcome}
                    </span>
                  )}
                </h2>
              </div>

              <div className="badges">
                {displayScore > 70 && (opp.directional_confidence || 50) >= 70 && <span className="badge" style={{backgroundColor: 'var(--accent-green)', color: '#000', fontWeight: 'bold'}}>🟢 BUY YES</span>}
                {displayScore > 70 && (opp.directional_confidence || 50) <= 30 && <span className="badge" style={{backgroundColor: 'var(--accent-rose)', color: '#fff', fontWeight: 'bold'}}>🔴 BUY NO</span>}
                {(opp.news_sentiment_score || 0) > 0.2 && <span className="badge bullish">Bullish News</span>}
                {(opp.news_sentiment_score || 0) < -0.2 && <span className="badge bearish">Bearish News</span>}
                {opp.volume > 1000000 && <span className="badge">Whale Vol</span>}
                {Array.isArray(opp.tags) && opp.tags.slice(0, 2).map(tag => (
                  <span key={tag} className="badge">{tag}</span>
                ))}
              </div>

              {displayNote && (
                <div className="llm-note">
                  " {displayNote} "
                </div>
              )}

              <div className="metrics">
                <div className="metric-pill">
                  <span className="metric-label">AI Score</span>
                  <span className="metric-value score">{displayScore > 1 ? displayScore.toFixed(1) : (displayScore * 100).toFixed(1)}</span>
                </div>
                <div className="metric-pill">
                  <span className="metric-label">Probability (Yes)</span>
                  <span className="metric-value" style={{color: 'var(--accent-green)'}}>
                    {opp.yes_price !== undefined ? (opp.yes_price * 100).toFixed(1) + '%' : 'N/A'}
                  </span>
                </div>
                <div className="metric-pill">
                  <span className="metric-label">Volume</span>
                  <span className="metric-value volume">{formatMoney(opp.volume)}</span>
                </div>
              </div>

              {/* L2 Order Book Depth */}
              <div>
                <div style={{display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-secondary)'}}>
                  <span>L2 Bids (Compradores)</span>
                  <span>L2 Asks (Vendedores)</span>
                </div>
                <div className="l2-bar-container" style={{ position: 'relative' }}>
                  <div className="l2-bids" style={{ width: `${bidPct}%`, display: 'flex', alignItems: 'center', paddingLeft: '4px', fontSize: '0.65rem', color: 'rgba(255,255,255,0.7)' }}>
                    {bidPct > 15 ? `${bidPct.toFixed(0)}%` : ''}
                  </div>
                  <div className="l2-asks" style={{ width: `${askPct}%`, display: 'flex', alignItems: 'center', justifyContent: 'flex-end', paddingRight: '4px', fontSize: '0.65rem', color: 'rgba(255,255,255,0.7)' }}>
                    {askPct > 15 ? `${askPct.toFixed(0)}%` : ''}
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </main>

      {selectedMarket && (
        <MarketModal 
          marketId={selectedMarket.id} 
          title={selectedMarket.event_title || selectedMarket.question || selectedMarket.title || "Market Details"} 
          onClose={() => setSelectedMarket(null)} 
        />
      )}
    </div>
  );
}
