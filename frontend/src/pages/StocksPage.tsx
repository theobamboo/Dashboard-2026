import PageHeader from '../components/PageHeader'
import { TrendingUp, BarChart2, Eye, Activity } from 'lucide-react'

function ComingSoon({ icon: Icon, title, desc }: { icon: React.ElementType; title: string; desc: string }) {
  return (
    <div className="glass rounded-xl p-6 flex flex-col items-center justify-center min-h-[180px] text-center border-dashed">
      <div className="w-12 h-12 rounded-xl bg-surface-2 flex items-center justify-center mb-3 border border-border-dim">
        <Icon size={20} className="text-accent-purple/70" />
      </div>
      <p className="text-text-secondary font-medium mb-1">{title}</p>
      <p className="text-text-muted text-xs">{desc}</p>
      <span className="mt-3 text-[10px] font-mono px-2 py-0.5 rounded border border-[#7c3aed]/30 text-[#7c3aed]/70">Layer 2</span>
    </div>
  )
}

export default function StocksPage() {
  return (
    <div className="space-y-6 max-w-[1600px]">
      <PageHeader
        title="Stocks &amp; ETFs"
        subtitle="yfinance · CBOE · Swing trade screener"
        badge="COMING SOON"
        badgeColor="#7c3aed"
      />
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: 'SPY', value: '—' }, { label: 'QQQ', value: '—' }, { label: 'VIX', value: '—' }, { label: 'Put/Call', value: '—' },
        ].map(s => (
          <div key={s.label} className="glass rounded-xl p-4 animate-pulse-slow">
            <p className="section-label mb-2">{s.label}</p>
            <p className="font-mono text-2xl font-bold text-text-muted">—</p>
          </div>
        ))}
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <ComingSoon icon={BarChart2}  title="TradingView Chart"    desc="Embedded chart with swing trade overlays" />
        <ComingSoon icon={Activity}   title="VIX Term Structure"   desc="CBOE VIX spot + futures curve" />
        <ComingSoon icon={Eye}        title="Put/Call Ratio"       desc="CBOE equity put/call ratio history" />
        <ComingSoon icon={TrendingUp} title="Momentum Screener"    desc="Volume breakout + momentum scanner" />
        <ComingSoon icon={BarChart2}  title="Sector ETF Flows"     desc="SPY/XLK/XLE/XLF rotation heatmap" />
        <ComingSoon icon={Activity}   title="Earnings Calendar"    desc="Upcoming high-impact earnings" />
      </div>
    </div>
  )
}
