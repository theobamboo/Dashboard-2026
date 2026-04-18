import PageHeader from '../components/PageHeader'
import StatCard from '../components/StatCard'
import TradingViewChart from '../components/TradingViewChart'
import { TrendingUp, BarChart2, Eye, Activity, DollarSign, Percent } from 'lucide-react'
import { useStocksOverview } from '../api/stocks'

function ComingSoon({ icon: Icon, title, desc, layer }: { icon: React.ElementType; title: string; desc: string; layer: string }) {
  return (
    <div className="glass rounded-xl p-6 flex flex-col items-center justify-center min-h-[180px] text-center border-dashed">
      <div className="w-12 h-12 rounded-xl bg-surface-2 flex items-center justify-center mb-3 border border-border-dim">
        <Icon size={20} className="text-accent-purple/70" />
      </div>
      <p className="text-text-secondary font-medium mb-1">{title}</p>
      <p className="text-text-muted text-xs">{desc}</p>
      <span className="mt-3 text-[10px] font-mono px-2 py-0.5 rounded border border-[#7c3aed]/30 text-[#7c3aed]/70">{layer}</span>
    </div>
  )
}

export default function StocksPage() {
  const { data, isLoading } = useStocksOverview()

  return (
    <div className="space-y-6 max-w-[1600px] animate-fade-in">
      <PageHeader
        title="Stocks & ETFs"
        subtitle="yfinance · CBOE · Swing trade screener"
        badge={data?.cached ? "CACHED" : "LIVE"}
        badgeColor="#7c3aed"
      />
      
      {/* ── Top stat row ── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="S&P 500 (SPY)"
          value={data?.assets['SPY'] ? `$${data.assets['SPY'].price.toFixed(2)}` : '—'}
          change={data?.assets['SPY']?.change_pct}
          loading={isLoading}
          icon={<DollarSign size={14} />}
        />
        <StatCard
          label="Nasdaq 100 (QQQ)"
          value={data?.assets['QQQ'] ? `$${data.assets['QQQ'].price.toFixed(2)}` : '—'}
          change={data?.assets['QQQ']?.change_pct}
          loading={isLoading}
          icon={<DollarSign size={14} />}
        />
        <StatCard
          label="Volatility Index (VIX)"
          value={data?.assets['^VIX'] ? `${data.assets['^VIX'].price.toFixed(2)}` : '—'}
          change={data?.assets['^VIX']?.change_pct}
          loading={isLoading}
          icon={<Percent size={14} />}
        />
        <StatCard
          label="Put/Call Ratio (CBOE)"
          value={data?.assets['PCR'] ? `${data.assets['PCR'].price.toFixed(2)}` : '—'}
          change={data?.assets['PCR']?.change_pct}
          loading={isLoading}
          icon={<Eye size={14} />}
        />
      </div>

      {/* ── TradingView Chart ── */}
      <TradingViewChart
        symbol="AMEX:SPY"
        label="SPY — S&P 500 ETF Advanced Chart"
        height={420}
      />

      {/* ── Coming soon panels ── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <ComingSoon icon={Activity}   title="VIX Term Structure"   desc="CBOE VIX spot + futures curve" layer="Layer 4" />
        <ComingSoon icon={Eye}        title="Put/Call Ratio"       desc="CBOE equity put/call ratio history" layer="Layer 4" />
        <ComingSoon icon={TrendingUp} title="Momentum Screener"    desc="Volume breakout + momentum scanner" layer="Layer 4" />
        <ComingSoon icon={BarChart2}  title="Sector ETF Flows"     desc="SPY/XLK/XLE/XLF rotation heatmap" layer="Layer 4" />
        <ComingSoon icon={Activity}   title="Earnings Calendar"    desc="Upcoming high-impact earnings" layer="Layer 4" />
      </div>
    </div>
  )
}
