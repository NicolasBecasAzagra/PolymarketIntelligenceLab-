"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Activity, LineChart } from "lucide-react";

export default function Navbar() {
  const pathname = usePathname();

  return (
    <nav style={{
      display: 'flex',
      gap: '1rem',
      justifyContent: 'center',
      padding: '1.5rem',
      borderBottom: '1px solid rgba(255,255,255,0.05)',
      marginBottom: '2rem'
    }}>
      <Link 
        href="/" 
        style={{
          display: 'flex', 
          alignItems: 'center', 
          gap: '0.5rem',
          padding: '0.5rem 1rem',
          borderRadius: '8px',
          background: pathname === '/' ? 'rgba(16, 185, 129, 0.1)' : 'transparent',
          color: pathname === '/' ? '#10b981' : 'var(--text-secondary)',
          textDecoration: 'none',
          fontWeight: pathname === '/' ? 600 : 400,
          transition: 'all 0.2s'
        }}
      >
        <Activity size={18} /> Live Radar
      </Link>
      
      <Link 
        href="/simulation" 
        style={{
          display: 'flex', 
          alignItems: 'center', 
          gap: '0.5rem',
          padding: '0.5rem 1rem',
          borderRadius: '8px',
          background: pathname === '/simulation' ? 'rgba(139, 92, 246, 0.1)' : 'transparent',
          color: pathname === '/simulation' ? '#8b5cf6' : 'var(--text-secondary)',
          textDecoration: 'none',
          fontWeight: pathname === '/simulation' ? 600 : 400,
          transition: 'all 0.2s'
        }}
      >
        <LineChart size={18} /> Simulation (Backtest)
      </Link>
    </nav>
  );
}
