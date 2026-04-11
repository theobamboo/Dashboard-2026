import PageHeader from '../components/PageHeader'
import { Globe2, BarChart3, ArrowUpDown, TrendingUp } from 'lucide-react'

function ComingSoon({ icon: Icon, title, desc }: { icon: React.ElementType; title: string; desc: string }) {
  return (
    <div className="glass rounded-xl p-6 flex flex-col items-center justify-center min-h-[180px] text-center border-dashed">
      <div className="w-12 h-12 rounded-xl bg-surface-2 flex items-center justify-center mb-3 border border-border-dim">
        <Icon size={20} className="text-gain/70" />
      </div>
      <p className="text-text-secondary font-medium mb-1">{title}</p>
      <p className="text-text-muted text-xs">{desc}</p>
      <span className="mt-3 text-[10px] font-mono px-2 py-0.5 rounded border border-gain/30 text-gain/70">Layer 2</span>
    </div>
  )
}

export default function FXPage() {
  return (
    <div className="space-y-6 max-w-[1600px]">
      <PageHeader
        title="FX Markets"
        subtitle="exchangerate.host · CFTC COT data · Carry ranking"
        badge="COMING SOON"
        badgeColor="#00ff88"
      />
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {['EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF'].map(pair => (
          <div key={pair} className="glass rounded-xl p-4">
            <p className="section-label mb-2">{pair}</p>
            <p className="font-mono text-2xl font-bold text-text-muted">—</p>
          </div>
        ))}
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <ComingSoon icon={Globe2}      title="Live FX Rates"       desc="Major & minor pairs via exchangerate.host" />
        <ComingSoon icon={BarChart3}   title="COT Positioning"     desc="CFTC Commitment of Traders weekly data" />
        <ComingSoon icon={TrendingUp}  title="Carry Trade Ranking" desc="Interest rate differential ranking" />
        <ComingSoon icon={ArrowUpDown} title="Correlation Matrix"  desc="Cross-pair 30d rolling correlation" />
        <ComingSoon icon={Globe2}      title="DXY vs Pairs"        desc="Dollar index correlation overlay" />
        <ComingSoon icon={BarChart3}   title="Volatility Surface"  desc="Implied volatility across major pairs" />
      </div>
    </div>
  )
}
