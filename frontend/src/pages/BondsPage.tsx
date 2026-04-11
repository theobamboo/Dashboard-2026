import PageHeader from '../components/PageHeader'
import { TrendingUp, Globe, BarChart3, DollarSign } from 'lucide-react'

function ComingSoon({ icon: Icon, title, desc }: { icon: React.ElementType; title: string; desc: string }) {
  return (
    <div className="glass rounded-xl p-6 flex flex-col items-center justify-center min-h-[180px] text-center border-dashed">
      <div className="w-12 h-12 rounded-xl bg-surface-2 flex items-center justify-center mb-3 border border-border-dim">
        <Icon size={20} className="text-neutral/70" />
      </div>
      <p className="text-text-secondary font-medium mb-1">{title}</p>
      <p className="text-text-muted text-xs">{desc}</p>
      <span className="mt-3 text-[10px] font-mono px-2 py-0.5 rounded border border-neutral/30 text-neutral/70">Layer 2</span>
    </div>
  )
}

export default function BondsPage() {
  return (
    <div className="space-y-6 max-w-[1600px]">
      <PageHeader
        title="Bonds &amp; Macro"
        subtitle="FRED API · DXY · Central bank rates · Yield curve"
        badge="COMING SOON"
        badgeColor="#f0a500"
      />
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: 'US 10Y Yield', value: '—' }, { label: '2Y/10Y Spread', value: '—' },
          { label: 'DXY', value: '—' }, { label: 'Fed Funds', value: '—' },
        ].map(s => (
          <div key={s.label} className="glass rounded-xl p-4">
            <p className="section-label mb-2">{s.label}</p>
            <p className="font-mono text-2xl font-bold text-text-muted">—</p>
          </div>
        ))}
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <ComingSoon icon={TrendingUp} title="Yield Curve"          desc="2Y/5Y/10Y/30Y Treasury curve via FRED" />
        <ComingSoon icon={Globe}      title="DXY Dollar Index"     desc="Dollar index + correlation overlay" />
        <ComingSoon icon={BarChart3}  title="Credit Spreads"       desc="IG & HY spreads from FRED" />
        <ComingSoon icon={DollarSign} title="Central Bank Rates"   desc="Fed, ECB, BOE, BOJ rate table" />
        <ComingSoon icon={TrendingUp} title="CPI / PCE Inflation"  desc="Rolling inflation data via FRED" />
        <ComingSoon icon={Globe}      title="Real Yields"          desc="TIPS / real yield vs nominal spread" />
      </div>
    </div>
  )
}
