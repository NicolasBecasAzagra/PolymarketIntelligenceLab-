"use client";

import { useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, AreaChart, Area } from "recharts";
import { Wallet, ArrowUpRight, ArrowDownRight, History } from "lucide-react";

interface Trade {
  timestamp: string;
  type: "BUY" | "SELL" | "BUY YES" | "BUY NO";
  title: string;
  price: number;
  shares: number;
  amount: number;
  pnl?: number;
}

interface PortfolioHistory {
  timestamp: string;
  value: number;
}

export default function SimulationPage() {
  const [history, setHistory] = useState<PortfolioHistory[]>([]);
  const [trades, setTrades] = useState<Trade[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`/api/simulation?t=${Date.now()}`)
      .then(res => res.json())
      .then(data => {
        if (data.status === "success") {
          // Format timestamps for display (YYYYMMDD_HH -> DD/MM HH:00)
          const formattedHistory = data.data.history.map((h: any) => {
            const day = h.timestamp.substring(6, 8);
            const month = h.timestamp.substring(4, 6);
            const hour = h.timestamp.split('_')[1];
            return {
              ...h,
              timeLabel: `${day}/${month} ${hour}:00`
            };
          });
          setHistory(formattedHistory);
          setTrades(data.data.trades);
        }
        setLoading(false);
      });
  }, []);

  const currentBalance = history.length > 0 ? history[history.length - 1].value : 3000;
  const pnl = currentBalance - 3000;
  const pnlPct = (pnl / 3000) * 100;

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 2rem 4rem 2rem' }}>
      
      <header style={{ textAlign: 'center', marginBottom: '3rem' }}>
        <h1 style={{ fontFamily: 'var(--font-display)', fontSize: '2.5rem', marginBottom: '0.5rem' }}>AI Trading Simulator</h1>
        <p style={{ color: 'var(--text-secondary)' }}>Backtesting historical predictions with a $3,000 mock portfolio</p>
      </header>

      {loading ? (
        <div className="loader">Running Simulation...</div>
      ) : (
        <>
          {/* Top Stats */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem', marginBottom: '3rem' }}>
            <div className="card" style={{ textAlign: 'center' }}>
              <div style={{ color: 'var(--text-secondary)', marginBottom: '0.5rem', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '0.5rem' }}>
                <Wallet size={18} /> Portfolio Value
              </div>
              <div style={{ fontSize: '2.5rem', fontWeight: 'bold', fontFamily: 'var(--font-display)' }}>
                ${currentBalance.toFixed(2)}
              </div>
            </div>

            <div className="card" style={{ textAlign: 'center' }}>
              <div style={{ color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>Total PNL</div>
              <div style={{ 
                fontSize: '2.5rem', 
                fontWeight: 'bold', 
                fontFamily: 'var(--font-display)',
                color: pnl >= 0 ? 'var(--accent-emerald)' : 'var(--accent-rose)'
              }}>
                {pnl >= 0 ? '+' : ''}${pnl.toFixed(2)} 
                <span style={{ fontSize: '1rem', marginLeft: '0.5rem' }}>({pnlPct.toFixed(2)}%)</span>
              </div>
            </div>

            <div className="card" style={{ textAlign: 'center' }}>
              <div style={{ color: 'var(--text-secondary)', marginBottom: '0.5rem', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '0.5rem' }}>
                <History size={18} /> Total Trades
              </div>
              <div style={{ fontSize: '2.5rem', fontWeight: 'bold', fontFamily: 'var(--font-display)' }}>
                {trades.length}
              </div>
            </div>
          </div>

          {/* Chart */}
          <div className="card" style={{ marginBottom: '3rem' }}>
            <h2 style={{ marginBottom: '1.5rem', fontSize: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              Equity Curve
            </h2>
            <div style={{ width: '100%', height: 400 }}>
              {history.length > 0 ? (
                <ResponsiveContainer>
                  <AreaChart data={history}>
                    <defs>
                      <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                    <XAxis dataKey="timeLabel" stroke="#a1a1aa" fontSize={12} />
                    <YAxis domain={['dataMin - 100', 'dataMax + 100']} stroke="#a1a1aa" fontSize={12} tickFormatter={(val) => `$${val}`} />
                    <Tooltip 
                      contentStyle={{ backgroundColor: 'rgba(10,10,10,0.9)', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '8px' }}
                      formatter={(value: any) => [`$${parseFloat(value).toFixed(2)}`, 'Portfolio Value']}
                    />
                    <Area type="monotone" dataKey="value" stroke="#8b5cf6" strokeWidth={3} fillOpacity={1} fill="url(#colorValue)" />
                  </AreaChart>
                </ResponsiveContainer>
              ) : (
                <div style={{ display: 'flex', height: '100%', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
                  Not enough historical data to chart yet. Let the bot run for a few hours.
                </div>
              )}
            </div>
          </div>

          {/* Ledger */}
          <div className="card">
            <h2 style={{ marginBottom: '1.5rem', fontSize: '1.25rem' }}>Trade Ledger</h2>
            
            {trades.length === 0 ? (
              <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '2rem' }}>No trades executed yet.</p>
            ) : (
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)', color: 'var(--text-secondary)' }}>
                      <th style={{ padding: '1rem' }}>Time</th>
                      <th style={{ padding: '1rem' }}>Type</th>
                      <th style={{ padding: '1rem' }}>Market</th>
                      <th style={{ padding: '1rem' }}>Price</th>
                      <th style={{ padding: '1rem' }}>Shares</th>
                      <th style={{ padding: '1rem' }}>Amount</th>
                      <th style={{ padding: '1rem', textAlign: 'right' }}>P/L</th>
                    </tr>
                  </thead>
                  <tbody>
                    {trades.map((t, i) => (
                      <tr key={i} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                        <td style={{ padding: '1rem', color: 'var(--text-muted)' }}>
                          {t.timestamp.split('_')[1] + ':00'}
                        </td>
                        <td style={{ padding: '1rem' }}>
                          {t.type.startsWith("BUY") ? (
                            <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.25rem', color: t.type === 'BUY YES' ? 'var(--accent-emerald)' : 'var(--accent-rose)', background: t.type === 'BUY YES' ? 'rgba(16,185,129,0.1)' : 'rgba(244,63,94,0.1)', padding: '0.25rem 0.5rem', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 600 }}>
                              <ArrowUpRight size={14} /> {t.type}
                            </span>
                          ) : (
                            <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.25rem', color: 'var(--text-primary)', background: 'rgba(255,255,255,0.1)', padding: '0.25rem 0.5rem', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 600 }}>
                              <ArrowDownRight size={14} /> SELL
                            </span>
                          )}
                        </td>
                        <td style={{ padding: '1rem', maxWidth: '400px', whiteSpace: 'normal', lineHeight: '1.4' }}>
                          {t.title}
                        </td>
                        <td style={{ padding: '1rem', fontFamily: 'var(--font-mono)' }}>
                          {(t.price * 100).toFixed(1)}¢
                        </td>
                        <td style={{ padding: '1rem', fontFamily: 'var(--font-mono)' }}>
                          {t.shares.toFixed(2)}
                        </td>
                        <td style={{ padding: '1rem', fontFamily: 'var(--font-mono)', fontWeight: 600 }}>
                          ${t.amount.toFixed(2)}
                        </td>
                        <td style={{ padding: '1rem', fontFamily: 'var(--font-mono)', fontWeight: 600, textAlign: 'right', color: t.pnl !== undefined && t.pnl !== 0 ? (t.pnl > 0 ? 'var(--accent-emerald)' : 'var(--accent-rose)') : 'var(--text-muted)' }}>
                          {t.pnl !== undefined && t.pnl !== 0 ? (t.pnl > 0 ? `+$${t.pnl.toFixed(2)}` : `-$${Math.abs(t.pnl).toFixed(2)}`) : '-'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
