"use client";

import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from 'recharts';
import { X, TrendingUp, Newspaper, Activity } from 'lucide-react';

interface HistoryPoint {
  timestamp: string;
  score: number;
  volume: number;
  price?: number;
}

interface NewsItem {
  title: string;
  summary: string;
  source: string;
  published_at: string;
}

interface MarketModalProps {
  marketId: string;
  title: string;
  onClose: () => void;
}

export default function MarketModal({ marketId, title, onClose }: MarketModalProps) {
  const [history, setHistory] = useState<HistoryPoint[]>([]);
  const [news, setNews] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch History & News simultaneously
    Promise.all([
      fetch(`/api/market/${marketId}/history`).then(r => r.ok ? r.json() : {data: []}),
      fetch(`/api/market/${marketId}/news`).then(r => r.ok ? r.json() : {data: []})
    ]).then(([histRes, newsRes]) => {
      // Format timestamps for graph
      const formattedHistory = (histRes.data || []).map((h: any) => {
        const scorePct = h.score > 1 ? h.score : h.score * 100;
        const pricePct = (h.price || 0) * 100;
        const day = h.timestamp.substring(6, 8);
        const month = h.timestamp.substring(4, 6);
        const hour = h.timestamp.split('_')[1];
        return {
          ...h,
          timeLabel: `${day}/${month} ${hour}:00`,
          scorePct: scorePct,
          pricePct: pricePct,
          buySignal: scorePct > 80 ? pricePct : null
        };
      });
      setHistory(formattedHistory);
      setNews(newsRes.data || []);
      setLoading(false);
    });
  }, [marketId]);

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        
        <button className="modal-close" onClick={onClose}>
          <X size={24} />
        </button>

        <h2 className="modal-title">{title}</h2>
        <div className="modal-badges">
          <span className="badge"><Activity size={14} /> Market Detail</span>
        </div>

        {loading ? (
          <div className="loader" style={{height: '300px'}}>Loading Intel...</div>
        ) : (
          <div className="modal-grid">
            
            {/* Left Column: Chart */}
            <div className="modal-chart-section">
              <h3><TrendingUp size={18} /> Market Evolution</h3>
              <div style={{ width: '100%', height: 300, marginTop: '1rem' }}>
                <ResponsiveContainer>
                  <LineChart data={history}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                    <XAxis dataKey="timeLabel" stroke="#a1a1aa" fontSize={12} />
                    <YAxis yAxisId="left" stroke="#8b5cf6" fontSize={12} domain={['auto', 'auto']} />
                    <YAxis yAxisId="right" orientation="right" stroke="#10b981" fontSize={12} domain={[0, 100]} unit="%" />
                    <Tooltip 
                      contentStyle={{ backgroundColor: 'rgba(10,10,10,0.9)', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '8px' }}
                    />
                    <Legend />
                    <Line yAxisId="left" type="monotone" dataKey="scorePct" stroke="#8b5cf6" strokeWidth={3} name="AI Score (0-100)" dot={{r:3}} />
                    <Line yAxisId="right" type="monotone" dataKey="pricePct" stroke="#10b981" strokeWidth={2} name="Yes Price (%)" dot={false} />
                    
                    {/* BUY Signals */}
                    <Line 
                      yAxisId="right"
                      type="monotone" 
                      dataKey="buySignal" 
                      stroke="none" 
                      name="BUY Signal"
                      isAnimationActive={true}
                      connectNulls={false}
                      dot={{ r: 8, fill: '#10b981', stroke: '#fff', strokeWidth: 2 }} 
                      activeDot={{ r: 10 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Right Column: News */}
            <div className="modal-news-section">
              <h3><Newspaper size={18} /> Live News Radar</h3>
              <div className="news-list">
                {news.length === 0 ? (
                  <p style={{color: 'var(--text-secondary)', fontStyle: 'italic', marginTop: '1rem'}}>No relevant news found in the last 24h.</p>
                ) : (
                  news.map((n, i) => (
                    <a key={i} href={n.source} target="_blank" rel="noreferrer" className="news-item">
                      <div className="news-title">{n.title}</div>
                      <div className="news-meta">
                        {new Date(n.published_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})} • 
                        <span className="news-domain"> {new URL(n.source).hostname.replace('www.','')}</span>
                      </div>
                    </a>
                  ))
                )}
              </div>
            </div>

          </div>
        )}
      </div>
    </div>
  );
}
