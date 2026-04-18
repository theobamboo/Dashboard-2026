import { useCryptoOverview, useFearGreed, usePrices } from '../api/crypto'
import StatCard from '../components/StatCard'
import PageHeader from '../components/PageHeader'
import BubbleChart from '../components/BubbleChart'
import TradingViewChart from '../components/TradingViewChart'
import { Bitcoin, Zap, Droplets, BarChart3 } from 'lucide-react'

// ── Fear & Greed Arc ──────────────────────────────────────────────────────
function FearGreedGauge({ value, classification }: { value: number; classification: string }) {
  // Map 0-100 to a colour sweep
  const getColor = (v: number) => {
    if (v <= 25) return '#ff3366'   // extreme fear
    if (v <= 45) return '#ff6b35'   // fear
    if (v <= 55) return '#f0a500'   // neutral
    if (v <= 75) return '#7ecb35'   // greed
    return '#00ff88'                 // extreme greed
  }

  const color = getColor(value)
  // SVG arc — 180° sweep
  const radius = 56
  const cx = 70
  const cy = 70
  const startAngle = 180
  const endAngle = startAngle + (value / 100) * 180
  const toRad = (deg: number) => (deg * Math.PI) / 180
  const x1 = cx + radius * Math.cos(toRad(startAngle))
  const y1 = cy + radius * Math.sin(toRad(startAngle))
  const x2 = cx + radius * Math.cos(toRad(endAngle))
  const y2 = cy + radius * Math.sin(toRad(endAngle))
  const largeArc = endAngle - startAngle > 180 ? 1 : 0

  return (
    <div className="glass rounded-xl p-5">
      <p className="section-label mb-4">Fear &amp; Greed Index</p>
      <div className="flex flex-col items-center">
        <svg width="140" height="80" viewBox="0 0 140 80">
          {/* Track */}
          <path
            d={`M ${cx - radius} ${cy} A ${radius} ${radius} 0 0 1 ${cx + radius} ${cy}`}
            fill="none" stroke="#1e2d45" strokeWidth="8" strokeLinecap="round"
          />
          {/* Value arc */}
          <path
            className="fg-arc"
            d={`M ${x1} ${y1} A ${radius} ${radius} 0 ${largeArc} 1 ${x2} ${y2}`}
            fill="none"
            stroke={color}
            strokeWidth="8"
            strokeLinecap="round"
            style={{ color }}
          />
          {/* Center value */}
          <text x={cx} y={cy - 4}   textAnchor="middle" fill={color}        fontSize="22" fontWeight="700" fontFamily="JetBrains Mono">{value}</text>
          <text x={cx} y={cy + 12}  textAnchor="middle" fill="#4a637a"      fontSize="8"  fontFamily="Inter">{classification.toUpperCase()}</text>
          {/* Scale labels */}
          <text x="10" y={cy + 16}  textAnchor="middle" fill="#4a637a" fontSize="7" fontFamily="Inter">0</text>
          <text x="130" y={cy + 16} textAnchor="middle" fill="#4a637a" fontSize="7" fontFamily="Inter">100</text>
        </svg>
        <div className="flex gap-4 mt-1 text-[10px] font-mono text-text-muted">
          <span className="text-loss">Extreme Fear</span>
          <span className="text-neutral">Neutral</span>
          <span className="text-gain">Extreme Greed</span>
        </div>
      </div>
    </div>
  )
}

// ── Top Coins Table ───────────────────────────────────────────────────────
function TopCoinsTable() {
  const { data, isLoading, isError } = usePrices(20)

  // Strictly validate that we received live data (not a stub response)
  const coins = Array.isArray(data?.coins) ? data.coins : null

  if (isLoading) {
    return (
      <div className="glass rounded-xl p-5">
        <p className="section-label mb-4">Top 20 Coins</p>
        <div className="space-y-2">
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="flex gap-4 animate-pulse">
              <div className="w-4 h-3 bg-surface-2 rounded" />
              <div className="w-24 h-3 bg-surface-2 rounded" />
              <div className="ml-auto w-20 h-3 bg-surface-2 rounded" />
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (isError || !coins) {
    return (
      <div className="glass rounded-xl p-5 flex flex-col items-center justify-center min-h-[200px]">
        <p className="text-text-muted text-sm">Unable to load coin data</p>
        <p className="text-text-muted/50 text-xs mt-1">Check backend connection</p>
      </div>
    )
  }

  return (
    <div className="glass rounded-xl overflow-hidden">
      <div className="px-5 py-4 border-b border-border-dim flex items-center justify-between">
        <p className="section-label">Top 20 Coins</p>
        <span className="text-[10px] text-text-muted font-mono">24h change</span>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b border-border-dim">
              <th className="text-left px-5 py-2.5 text-text-muted font-medium w-8">#</th>
              <th className="text-left px-3 py-2.5 text-text-muted font-medium">Coin</th>
              <th className="text-right px-3 py-2.5 text-text-muted font-medium">Price</th>
              <th className="text-right px-3 py-2.5 text-text-muted font-medium">1h</th>
              <th className="text-right px-3 py-2.5 text-text-muted font-medium">24h</th>
              <th className="text-right px-3 py-2.5 text-text-muted font-medium">7d</th>
              <th className="text-right px-5 py-2.5 text-text-muted font-medium">Market Cap</th>
            </tr>
          </thead>
          <tbody>
            {coins.map((coin) => {
              const fmt = (v: number | null | undefined) => {
                if (v == null) return <span className="text-text-muted">—</span>
                const cls = v > 0 ? 'text-gain' : v < 0 ? 'text-loss' : 'text-text-muted'
                return <span className={`font-mono ${cls}`}>{v > 0 ? '+' : ''}{v.toFixed(2)}%</span>
              }

              const fmtPrice = (p: number) => p >= 1
                ? p.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
                : p.toLocaleString('en-US', { minimumFractionDigits: 4, maximumFractionDigits: 6 })

              const fmtMcap = (m: number) => {
                if (m >= 1e12) return `$${(m / 1e12).toFixed(2)}T`
                if (m >= 1e9)  return `$${(m / 1e9).toFixed(1)}B`
                return `$${(m / 1e6).toFixed(0)}M`
              }

              return (
                <tr key={coin.id} className="border-b border-border-dim/50 hover:bg-white/[0.02] transition-colors">
                  <td className="px-5 py-2.5 text-text-muted font-mono">{coin.market_cap_rank}</td>
                  <td className="px-3 py-2.5">
                    <div className="flex items-center gap-2">
                      <img src={coin.image} alt={coin.symbol} className="w-5 h-5 rounded-full" loading="lazy" />
                      <span className="text-text-primary font-medium">{coin.name}</span>
                      <span className="text-text-muted font-mono uppercase">{coin.symbol}</span>
                    </div>
                  </td>
                  <td className="px-3 py-2.5 text-right font-mono text-text-primary">${fmtPrice(coin.current_price)}</td>
                  <td className="px-3 py-2.5 text-right">{fmt(coin.price_change_percentage_1h)}</td>
                  <td className="px-3 py-2.5 text-right">{fmt(coin.price_change_percentage_24h)}</td>
                  <td className="px-3 py-2.5 text-right">{fmt(coin.price_change_percentage_7d)}</td>
                  <td className="px-5 py-2.5 text-right font-mono text-text-secondary">{fmtMcap(coin.market_cap)}</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}

// ── Placeholder panels ────────────────────────────────────────────────────
function StubPanel({ icon: Icon, title, description, layer }: {
  icon: React.ElementType; title: string; description: string; layer: string
}) {
  return (
    <div className="glass rounded-xl p-5 flex flex-col items-center justify-center min-h-[160px] border-dashed text-center">
      <div className="w-10 h-10 rounded-lg bg-surface-2 flex items-center justify-center mb-3">
        <Icon size={18} className="text-text-muted" />
      </div>
      <p className="text-text-secondary text-sm font-medium mb-1">{title}</p>
      <p className="text-text-muted text-xs mb-2">{description}</p>
      <span className="text-[10px] font-mono px-2 py-0.5 rounded border border-accent-cyan/30 text-accent-cyan/70">{layer}</span>
    </div>
  )
}

// ── Main Page ─────────────────────────────────────────────────────────────
export default function CryptoPage() {
  const { data: overview, isLoading: ovLoading } = useCryptoOverview()
  const { data: fg,       isLoading: fgLoading  } = useFearGreed(7)

  const fmtMcap = (v?: number) => {
    if (!v) return '—'
    if (v >= 1e12) return `$${(v / 1e12).toFixed(2)}T`
    return `$${(v / 1e9).toFixed(0)}B`
  }

  return (
    <div className="space-y-6 animate-fade-in max-w-[1600px]">
      <PageHeader
        title="Crypto Markets"
        subtitle="Real-time overview · CoinGecko · Alternative.me"
        badge="LIVE"
        badgeColor="#00d4ff"
      />

      {/* ── Top stat row ── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="BTC Dominance"
          value={overview ? `${overview.btc_dominance.toFixed(2)}%` : '—'}
          icon={<Bitcoin size={14} />}
          loading={ovLoading}
          variant="default"
        />
        <StatCard
          label="ETH Dominance"
          value={overview ? `${overview.eth_dominance.toFixed(2)}%` : '—'}
          loading={ovLoading}
          variant="default"
        />
        <StatCard
          label="Total Market Cap"
          value={fmtMcap(overview?.total_market_cap_usd)}
          change={overview?.market_cap_change_24h_pct}
          loading={ovLoading}
        />
        <StatCard
          label="Fear & Greed"
          value={fg?.current.value ?? '—'}
          subValue={fg?.current.classification}
          loading={fgLoading}
          variant={
            fg ? (fg.current.value <= 25 ? 'loss' : fg.current.value >= 75 ? 'gain' : 'neutral') : 'default'
          }
        />
      </div>

      {/* ── Bubble Chart — full width ── */}
      <BubbleChart />

      {/* ── TradingView Chart ── */}
      <TradingViewChart
        symbol="BINANCE:BTCUSDT"
        label="BTC / USDT — Advanced Chart"
        height={420}
      />

      {/* ── Lower row — F&G gauge + table + stubs ── */}
      <div className="grid grid-cols-1 xl:grid-cols-4 gap-4">
        {/* Left column: F&G gauge + stub panels */}
        <div className="space-y-4">
          {fgLoading ? (
            <div className="glass rounded-xl p-5 animate-pulse">
              <div className="h-3 w-28 bg-surface-2 rounded mb-4" />
              <div className="h-24 bg-surface-2 rounded" />
            </div>
          ) : fg ? (
            <FearGreedGauge value={fg.current.value} classification={fg.current.classification} />
          ) : null}
          <StubPanel
            icon={Zap}
            title="Funding Rates"
            description="Perpetual futures funding rates across major exchanges via CoinGlass"
            layer="Layer 3"
          />
          <StubPanel
            icon={Droplets}
            title="Liquidations Heatmap"
            description="Real-time liquidation levels from CoinGlass"
            layer="Layer 3"
          />
          <StubPanel
            icon={BarChart3}
            title="Open Interest"
            description="Aggregated OI across BTC/ETH perps"
            layer="Layer 3"
          />
        </div>

        {/* Top coins table spans remaining 3 cols */}
        <div className="xl:col-span-3">
          <TopCoinsTable />
        </div>
      </div>
    </div>
  )
}
