import PageHeader from '../components/PageHeader'
import StatCard from '../components/StatCard'
import TradingViewChart from '../components/TradingViewChart'
import { TrendingUp, Globe, BarChart3, DollarSign, Activity, Compass, AlertTriangle } from 'lucide-react'
import { useFxOverview } from '../api/fx'

function ComingSoon({ icon: Icon, title, desc, layer }: {
  icon: React.ElementType; title: string; desc: string; layer: string
}) {
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

/** Safely format a rate value — never throws */
function fmtRate(price: number | null | undefined): string {
  if (price == null || isNaN(price) || price === 0) return '—'
  return price >= 10 ? price.toFixed(2) : price.toFixed(4)
}

const FX_PAIRS = ['EUR/USD', 'GBP/USD', 'USD/JPY', 'GBP/EUR', 'USD/CHF', 'AUD/USD'] as const

export default function FXPage() {
  const { data, isLoading, isError, error } = useFxOverview()

  // ── Hard error state — backend unreachable or returned 5xx ──────────────
  if (isError) {
    return (
      <div className="space-y-6 max-w-[1600px] animate-fade-in">
        <PageHeader
          title="FX Markets"
          subtitle="exchangerate.host · yfinance · CFTC Data"
          badge="ERROR"
          badgeColor="#ff3366"
        />
        <div className="glass rounded-xl p-10 flex flex-col items-center justify-center min-h-[300px] text-center">
          <AlertTriangle size={36} className="text-[#ff3366] mb-4" />
          <p className="text-text-secondary font-medium mb-2">Unable to load FX data</p>
          <p className="text-text-muted text-xs mb-4">
            {error instanceof Error ? error.message : 'Backend connection failed — check that the server is running on port 8000'}
          </p>
          <span className="text-[10px] font-mono px-3 py-1 rounded border border-[#ff3366]/30 text-[#ff3366]/70">
            GET /fx/overview → failed
          </span>
        </div>

        {/* Chart still renders without backend data — it's client-side only */}
        <TradingViewChart
          symbol="FX:EURUSD"
          label="EUR / USD — Advanced Chart"
          height={420}
        />
      </div>
    )
  }

  // ── Safe rate accessor — never crashes on missing keys ───────────────────
  const getRate = (pair: string) => data?.rates?.[pair]
  const getDxyPrice = () => data?.dxy?.price ?? null
  const getDxyChange = () => data?.dxy?.change_pct ?? null

  return (
    <div className="space-y-6 max-w-[1600px] animate-fade-in">
      <PageHeader
        title="FX Markets"
        subtitle="exchangerate.host · yfinance · CFTC Data"
        badge={isLoading ? 'LOADING' : data?.cached ? 'CACHED' : 'LIVE'}
        badgeColor="#f0a500"
      />

      {/* ── Top stat row ── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {FX_PAIRS.map((pair) => {
          const rate = getRate(pair)
          return (
            <StatCard
              key={pair}
              label={pair}
              value={fmtRate(rate?.price)}
              change={rate?.change_pct ?? null}
              loading={isLoading}
              icon={<Globe size={14} />}
            />
          )
        })}

        <StatCard
          label="DXY Dollar Index"
          value={getDxyPrice() != null ? `${getDxyPrice()!.toFixed(2)}` : '—'}
          change={getDxyChange()}
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
