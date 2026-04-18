import PageHeader from '../components/PageHeader'
import StatCard from '../components/StatCard'
import TradingViewChart from '../components/TradingViewChart'
import { TrendingUp, Globe, BarChart3, DollarSign, Percent, Briefcase } from 'lucide-react'
import { useBondsOverview } from '../api/bonds'

function ComingSoon({ icon: Icon, title, desc, layer }: { icon: React.ElementType; title: string; desc: string; layer: string }) {
  return (
    <div className="glass rounded-xl p-6 flex flex-col items-center justify-center min-h-[180px] text-center border-dashed">
      <div className="w-12 h-12 rounded-xl bg-surface-2 flex items-center justify-center mb-3 border border-border-dim">
        <Icon size={20} className="text-[#00d4ff]/70" />
      </div>
      <p className="text-text-secondary font-medium mb-1">{title}</p>
      <p className="text-text-muted text-xs">{desc}</p>
      <span className="mt-3 text-[10px] font-mono px-2 py-0.5 rounded border border-[#00d4ff]/30 text-[#00d4ff]/70">{layer}</span>
    </div>
  )
}

export default function BondsPage() {
  const { data, isLoading } = useBondsOverview()

  const safeVal = (key: string) => data?.macro?.[key]?.value
  const safeChange = (key: string) => data?.macro?.[key]?.change

  return (
    <div className="space-y-6 max-w-[1600px] animate-fade-in">
      <PageHeader
        title="Bonds &amp; Macro"
        subtitle="FRED · yfinance · USD &amp; Yields"
        badge={data?.cached ? "CACHED" : "LIVE"}
        badgeColor="#00d4ff"
      />
      
      {/* ── Top stat row ── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="US 2Y Yield"
          value={safeVal('DGS2') !== undefined ? `${safeVal('DGS2')!.toFixed(2)}%` : '—'}
          change={safeChange('DGS2')}
          loading={isLoading}
          icon={<Percent size={14} />}
        />
        <StatCard
          label="US 10Y Yield"
          value={safeVal('DGS10') !== undefined ? `${safeVal('DGS10')!.toFixed(2)}%` : '—'}
          change={safeChange('DGS10')}
          loading={isLoading}
          icon={<Percent size={14} />}
        />
        <StatCard
          label="2s10s Spread"
          value={safeVal('2s10s_spread') !== undefined ? `${safeVal('2s10s_spread')!.toFixed(2)}%` : '—'}
          change={safeChange('2s10s_spread')}
          loading={isLoading}
          icon={<TrendingUp size={14} />}
        />
        <StatCard
          label="DXY Dollar Index"
          value={data?.dxy?.price !== undefined ? `${data.dxy.price.toFixed(2)}` : '—'}
          change={data?.dxy?.change_pct}
          loading={isLoading}
          icon={<DollarSign size={14} />}
        />
        <StatCard
          label="US CPI"
          value={safeVal('CPIAUCSL') !== undefined ? `${safeVal('CPIAUCSL')!.toFixed(1)}` : '—'}
          change={safeChange('CPIAUCSL')}
          loading={isLoading}
          icon={<BarChart3 size={14} />}
        />
        <StatCard
          label="Fed Funds Rate"
          value={safeVal('FEDFUNDS') !== undefined ? `${safeVal('FEDFUNDS')!.toFixed(2)}%` : '—'}
          change={safeChange('FEDFUNDS')}
          loading={isLoading}
          icon={<Globe size={14} />}
        />
        <StatCard
          label="Unemployment"
          value={safeVal('UNRATE') !== undefined ? `${safeVal('UNRATE')!.toFixed(1)}%` : '—'}
          change={safeChange('UNRATE')}
          loading={isLoading}
          icon={<Briefcase size={14} />}
        />
        <StatCard
          label="US 30Y Yield"
          value={safeVal('DGS30') !== undefined ? `${safeVal('DGS30')!.toFixed(2)}%` : '—'}
          change={safeChange('DGS30')}
          loading={isLoading}
          icon={<Percent size={14} />}
        />
      </div>

      {/* ── TradingView Chart ── */}
      <TradingViewChart
        symbol="TVC:US10Y"
        label="US 10-Year Treasury Yield — Advanced Chart"
        height={420}
      />

      {/* ── Coming soon panels ── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <ComingSoon icon={TrendingUp} title="Yield Curve Chart"    desc="Interactive 2Y/5Y/10Y/30Y curve" layer="Layer 5" />
        <ComingSoon icon={Globe}      title="DXY Correlation"      desc="Dollar vs SPY/BTC rolling window" layer="Layer 5" />
        <ComingSoon icon={BarChart3}  title="Credit Spreads"       desc="IG &amp; HY spreads from FRED" layer="Layer 5" />
        <ComingSoon icon={DollarSign} title="Central Bank Rates"   desc="Fed, ECB, BOE, BOJ rate table" layer="Layer 5" />
        <ComingSoon icon={TrendingUp} title="Inflation Trends"     desc="CPI vs Core PCE breakdown" layer="Layer 5" />
        <ComingSoon icon={Globe}      title="Real Yields"          desc="TIPS / real yield vs nominal" layer="Layer 5" />
      </div>
    </div>
  )
}
