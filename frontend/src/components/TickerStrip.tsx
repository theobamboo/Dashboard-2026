import { usePrices, useDominance } from '../api/crypto'
import { TrendingUp, TrendingDown } from 'lucide-react'

interface TickerItem {
  symbol: string
  price: number
  change: number
}

function TickerCell({ item }: { item: TickerItem }) {
  const isGain = item.change >= 0
  return (
    <span className="inline-flex items-center gap-2 px-5 border-r border-border-dim/50 last:border-r-0">
      <span className="text-text-muted text-xs font-mono uppercase">{item.symbol}</span>
      <span className="text-text-primary font-mono text-xs font-medium">
        {item.price.toLocaleString('en-US', {
          minimumFractionDigits: item.price < 10 ? 4 : item.price < 1000 ? 2 : 0,
          maximumFractionDigits: item.price < 10 ? 4 : item.price < 1000 ? 2 : 0,
        })}
      </span>
      <span className={`inline-flex items-center gap-0.5 text-[10px] font-mono font-semibold ${isGain ? 'text-gain' : 'text-loss'}`}>
        {isGain ? <TrendingUp size={9} /> : <TrendingDown size={9} />}
        {isGain ? '+' : ''}{item.change.toFixed(2)}%
      </span>
    </span>
  )
}

// Skeleton while loading or on error
function TickerSkeleton() {
  return (
    <div className="flex-1 overflow-hidden flex items-center px-4">
      <div className="flex gap-8">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="flex gap-2 items-center">
            <div className="w-8 h-2 bg-surface-2 rounded animate-pulse" />
            <div className="w-14 h-2 bg-surface-2 rounded animate-pulse" />
          </div>
        ))}
      </div>
    </div>
  )
}

export default function TickerStrip() {
  const { data: prices, isError: pricesError } = usePrices(10)
  const { data: dom,    isError: domError }    = useDominance()

  // Guard: loading or error state
  if (!prices || !dom || pricesError || domError) return <TickerSkeleton />

  // Guard: API might return a stub object (status: "not_implemented") instead of the expected shape
  if (!Array.isArray(prices.coins) || typeof dom.btc_dominance !== 'number') return <TickerSkeleton />

  const items: TickerItem[] = prices.coins.map(c => ({
    symbol: c.symbol?.toUpperCase() ?? '?',
    price: c.current_price ?? 0,
    change: c.price_change_percentage_24h ?? 0,
  }))

  const extras: TickerItem[] = [
    { symbol: 'BTC.D', price: dom.btc_dominance,                 change: 0 },
    { symbol: 'MCAP',  price: dom.total_market_cap_usd / 1e12,   change: dom.market_cap_change_24h_pct ?? 0 },
  ]

  const all = [...items, ...extras]
  const doubled = [...all, ...all] // duplicate for seamless CSS loop

  return (
    <div className="flex-1 ticker-wrap">
      <div className="ticker-inner">
        {doubled.map((item, i) => (
          <TickerCell key={`${item.symbol}-${i}`} item={item} />
        ))}
      </div>
    </div>
  )
}
