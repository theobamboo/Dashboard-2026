import PageHeader from '../components/PageHeader'
import StatCard from '../components/StatCard'
import TradingViewChart from '../components/TradingViewChart'
import { TrendingUp, Globe, BarChart3, DollarSign, Activity, Compass } from 'lucide-react'
import { useFxOverview } from '../api/fx'

function ComingSoon({ icon: Icon, title, desc, layer }: { icon: React.ElementType; title: string; desc: string; layer: string }) {
  return (
    <div className="glass rounded-xl p-6 flex flex-col items-center justify-center min-h-[180px] text-center border-dashed">
      <div className="w-12 h-12 rounded-xl bg-surface-2 flex items-center justify-center mb-3 border border-border-dim">
        <Icon size={20} className="text-[#f0a500]/70" />
      </div>
      <p className="text-text-secondary font-medium mb-1">{title}</p>
      <p className="text-text-muted text-xs">{desc}</p>
      <span className="mt-3 text-[10px] font-mono px-2 py-0.5 rounded border border-[#f0a500]/30 text-[#f0a500]/70">{layer}</span>
    </div>
  )
}

export default function FXPage() {
  const { data, isLoading } = useFxOverview()

  return (
    <div className="space-y-6 max-w-[1600px] animate-fade-in">
      <PageHeader
        title="FX Markets"
        subtitle="exchangerate.host · yfinance · CFTC Data"
        badge={data?.cached ? "CACHED" : "LIVE"}
        badgeColor="#f0a500"
      />
      
      {/* ── Top stat row ── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {['EUR/USD', 'GBP/USD', 'USD/JPY', 'GBP/EUR', 'USD/CHF', 'AUD/USD'].map((pair) => (
          <StatCard
            key={pair}
            label={pair}
            value={data?.rates?.[pair]?.price != null ? `${data.rates[pair].price >= 10 ? data.rates[pair].price.toFixed(2) : data.rates[pair].price.toFixed(4)}` : '—'}
            change={data?.rates?.[pair]?.change_pct}
            loading={isLoading}
            icon={<Globe size={14} />}
          />
        ))}

        <StatCard
          label="DXY Dollar Index"
          value={data?.dxy?.price != null ? `${data.dxy.price.toFixed(2)}` : '—'}
          change={data?.dxy?.change_pct}
          loading={isLoading}
          icon={<DollarSign size={14} />}
        />
        
        <StatCard
          label="Volatility Index"
          value="—"
          change={null}
          loading={isLoading}
          icon={<Activity size={14} />}
        />
      </div>

      {/* ── TradingView Chart ── */}
      <TradingViewChart
        symbol="FX:EURUSD"
        label="EUR / USD — Advanced Chart"
        height={420}
      />

      {/* ── Coming soon panels ── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <ComingSoon icon={TrendingUp} title="DXY Correlation Matrix" desc="Live correlation heatmaps for major pairs" layer="Layer 6" />
        <ComingSoon icon={BarChart3}  title="CFTC COT Positioning"   desc="Commitment of Traders weekly bias" layer="Layer 6" />
        <ComingSoon icon={Compass}    title="Carry Trade Ranking"    desc="Interest rate differentials vs Volatility" layer="Layer 6" />
      </div>
    </div>
  )
}
