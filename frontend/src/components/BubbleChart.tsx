/**
 * BubbleChart.tsx
 * CryptoBubbles-style D3.js force-directed packed circle visualization.
 *
 * Features:
 *  - Bubble size = market cap (sqrt scale, log-compressed)
 *  - Bubble colour = % price change (red → neutral → green)
 *  - 3D sphere sheen via SVG radialGradient overlay
 *  - Timeframe tabs: 1H | 24H | 7D
 *  - Force simulation (collision + centering) — runs synchronously then freezes
 *  - Smooth colour transitions on timeframe switch
 *  - Rich hover tooltip
 *  - Responsive SVG (viewBox-based)
 */

import { useRef, useEffect, useState, useCallback } from 'react'
import * as d3 from 'd3'
import { usePrices, type CoinPrice } from '../api/crypto'

// ── Constants ────────────────────────────────────────────────────────────────

const VW = 1400   // SVG viewBox width
const VH = 580    // SVG viewBox height

type Timeframe = '1h' | '24h' | '7d'

const TF_LABELS: { key: Timeframe; label: string }[] = [
  { key: '1h',  label: '1H'  },
  { key: '24h', label: '24H' },
  { key: '7d',  label: '7D'  },
]

// ── Helpers ──────────────────────────────────────────────────────────────────

function getPct(coin: CoinPrice, tf: Timeframe): number {
  switch (tf) {
    case '1h':  return coin.price_change_percentage_1h  ?? 0
    case '24h': return coin.price_change_percentage_24h ?? 0
    case '7d':  return coin.price_change_percentage_7d  ?? 0
  }
}

/** Returns a hex colour for a given % change (-∞…+∞). */
function pctToColor(pct: number): string {
  const clamped = Math.max(-20, Math.min(20, pct))
  if (Math.abs(clamped) < 0.05) return '#1a2535'
  if (clamped > 0) {
    const t = Math.min(clamped / 12, 1)
    return d3.interpolateRgb('#0d2a1a', '#00cc66')(t as number)
  }
  const t = Math.min(Math.abs(clamped) / 12, 1)
  return d3.interpolateRgb('#2a0d16', '#e02052')(t as number)
}

/** Returns the border stroke colour (brighter than fill). */
function pctToStroke(pct: number): string {
  if (Math.abs(pct) < 0.05) return '#2a3f5c'
  return pct > 0 ? '#00ff88' : '#ff3366'
}

/** Formats a price for tooltip. */
function fmtPrice(p: number): string {
  if (p >= 1000) return `$${p.toLocaleString('en-US', { maximumFractionDigits: 0 })}`
  if (p >= 1)    return `$${p.toFixed(2)}`
  return `$${p.toFixed(5)}`
}

/** Formats market cap for tooltip. */
function fmtMcap(m: number): string {
  if (m >= 1e12) return `$${(m / 1e12).toFixed(2)}T`
  if (m >= 1e9)  return `$${(m / 1e9).toFixed(1)}B`
  return `$${(m / 1e6).toFixed(0)}M`
}

// ── Node type ────────────────────────────────────────────────────────────────

interface BubbleNode extends d3.SimulationNodeDatum {
  id: string
  symbol: string
  name: string
  image: string
  price: number
  marketCap: number
  r: number                // computed radius (px in viewBox coords)
}

// ── Tooltip state ────────────────────────────────────────────────────────────

interface TooltipState {
  visible: boolean
  x: number
  y: number
  coin: BubbleNode | null
  pct: number
}

// ── Component ────────────────────────────────────────────────────────────────

export default function BubbleChart() {
  const svgRef    = useRef<SVGSVGElement>(null)
  const nodesRef  = useRef<BubbleNode[]>([])  // stable node array (simulation mutates x/y)
  const simRef    = useRef<d3.Simulation<BubbleNode, undefined> | null>(null)
  const tfRef     = useRef<Timeframe>('24h')

  const [tf, setTfState]         = useState<Timeframe>('24h')
  const [ready, setReady]        = useState(false)
  const [tooltip, setTooltip]    = useState<TooltipState>({ visible: false, x: 0, y: 0, coin: null, pct: 0 })

  const { data, isLoading, isError } = usePrices(100)

  // ── Radius scale (built once, stable) ──────────────────────────────────────
  const rScale = useCallback((coins: CoinPrice[]) => {
    const mcaps = coins.map(c => c.market_cap).filter(Boolean)
    const [minM, maxM] = d3.extent(mcaps) as [number, number]
    // log-compress the range so BTC doesn't eat everything
    return d3.scaleSqrt()
      .domain([Math.sqrt(minM), Math.sqrt(maxM)])
      .range([22, 88])
      .clamp(true)
  }, [])

  // ── Build / update SVG via D3 ──────────────────────────────────────────────
  useEffect(() => {
    if (!data || !Array.isArray(data.coins) || !svgRef.current) return

    const svg    = d3.select(svgRef.current)
    const coins  = data.coins
    const scale  = rScale(coins)

    // ── First time: build nodes + run simulation ───────────────────────────
    if (nodesRef.current.length === 0) {
      nodesRef.current = coins.map(c => ({
        id:        c.id,
        symbol:    c.symbol.toUpperCase(),
        name:      c.name,
        image:     c.image,
        price:     c.current_price,
        marketCap: c.market_cap,
        r:         scale(Math.sqrt(c.market_cap)),
        x:         VW / 2 + (Math.random() - 0.5) * 200,
        y:         VH / 2 + (Math.random() - 0.5) * 200,
      }))

      const sim = d3.forceSimulation<BubbleNode>(nodesRef.current)
        .force('center',  d3.forceCenter(VW / 2, VH / 2).strength(0.08))
        .force('collide', d3.forceCollide<BubbleNode>(d => d.r + 2.5).strength(0.85).iterations(3))
        .force('charge',  d3.forceManyBody().strength(6))
        .alphaDecay(0.02)
        .stop()

      // Run synchronously — avoids layout thrash
      for (let i = 0; i < 350; i++) sim.tick()

      simRef.current = sim
      buildSVG(svg, nodesRef.current, coins, tfRef.current)
      setReady(true)
    } else {
      // Subsequent renders (data refresh) — update colours only
      updateColors(svg, coins, tfRef.current)
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [data])

  // ── Timeframe change: update colours only (positions are stable) ───────────
  const setTf = useCallback((newTf: Timeframe) => {
    setTfState(newTf)
    tfRef.current = newTf
    if (!data || !svgRef.current) return
    updateColors(d3.select(svgRef.current), data.coins, newTf)
  }, [data])

  // ── D3 helpers ─────────────────────────────────────────────────────────────

  function buildSVG(
    svg: d3.Selection<SVGSVGElement, unknown, null, undefined>,
    nodes: BubbleNode[],
    coins: CoinPrice[],
    currentTf: Timeframe,
  ) {
    svg.selectAll('*').remove()

    // Defs: sheen gradient + clip paths
    const defs = svg.append('defs')

    // Single shared sheen gradient (simulates light from top-left)
    defs.append('radialGradient')
      .attr('id', 'bubble-sheen')
      .attr('cx', '32%').attr('cy', '28%').attr('r', '65%')
      .call(g => {
        g.append('stop').attr('offset', '0%')  .attr('stop-color', 'rgba(255,255,255,0.30)')
        g.append('stop').attr('offset', '55%') .attr('stop-color', 'rgba(255,255,255,0.04)')
        g.append('stop').attr('offset', '100%').attr('stop-color', 'rgba(0,0,0,0.18)')
      })

    // Dark rim gradient
    defs.append('radialGradient')
      .attr('id', 'bubble-rim')
      .attr('cx', '50%').attr('cy', '50%').attr('r', '50%')
      .call(g => {
        g.append('stop').attr('offset', '70%') .attr('stop-color', 'rgba(0,0,0,0)')
        g.append('stop').attr('offset', '100%').attr('stop-color', 'rgba(0,0,0,0.25)')
      })

    // Coin lookup map for fast pct access
    const coinMap = new Map(coins.map(c => [c.id, c]))

    // Bubble groups
    const groups = svg.selectAll<SVGGElement, BubbleNode>('g.bubble')
      .data(nodes, d => d.id)
      .join('g')
      .attr('class', 'bubble')
      .attr('transform', d => `translate(${d.x},${d.y})`)
      .style('cursor', 'pointer')

    // Base coloured circle
    groups.append('circle')
      .attr('class', 'base')
      .attr('r', d => d.r)
      .attr('fill',   d => pctToColor(getPct(coinMap.get(d.id)!, currentTf)))
      .attr('stroke', d => pctToStroke(getPct(coinMap.get(d.id)!, currentTf)))
      .attr('stroke-width', d => d.r > 35 ? 1.5 : 0.8)
      .attr('stroke-opacity', 0.6)
      .style('transition', 'fill 0.5s ease, stroke 0.5s ease')

    // Sheen overlay
    groups.append('circle')
      .attr('r', d => d.r)
      .attr('fill', 'url(#bubble-sheen)')
      .attr('pointer-events', 'none')

    // Rim overlay
    groups.append('circle')
      .attr('r', d => d.r)
      .attr('fill', 'url(#bubble-rim)')
      .attr('pointer-events', 'none')

    // Symbol text
    groups.filter(d => d.r >= 22)
      .append('text')
      .attr('class', 'sym')
      .attr('text-anchor', 'middle')
      .attr('dy', d => d.r >= 40 ? '-5' : '3')
      .attr('fill', '#ffffff')
      .attr('font-size', d => Math.min(d.r * 0.42, 18))
      .attr('font-weight', '700')
      .attr('font-family', 'Inter, sans-serif')
      .attr('pointer-events', 'none')
      .attr('paint-order', 'stroke')
      .attr('stroke', 'rgba(0,0,0,0.4)')
      .attr('stroke-width', 3)
      .text(d => d.r < 28 ? d.symbol.slice(0, 3) : d.symbol)

    // Pct text
    groups.filter(d => d.r >= 38)
      .append('text')
      .attr('class', 'pct')
      .attr('text-anchor', 'middle')
      .attr('dy', '14')
      .attr('fill', 'rgba(255,255,255,0.85)')
      .attr('font-size', d => Math.min(d.r * 0.30, 13))
      .attr('font-weight', '500')
      .attr('font-family', '"JetBrains Mono", monospace')
      .attr('pointer-events', 'none')
      .attr('paint-order', 'stroke')
      .attr('stroke', 'rgba(0,0,0,0.4)')
      .attr('stroke-width', 2)
      .text(d => {
        const pct = getPct(coinMap.get(d.id)!, currentTf)
        return `${pct >= 0 ? '+' : ''}${pct.toFixed(2)}%`
      })

    // Hover interactions (use raw SVG events for performance)
    groups
      .on('mouseenter', function(event: MouseEvent, d: BubbleNode) {
        d3.select(this).select('.base')
          .attr('stroke-opacity', 1)
          .attr('stroke-width', 2.5)
        const coin = coinMap.get(d.id)!
        const pct  = getPct(coin, tfRef.current)
        const rect = (svgRef.current as SVGSVGElement).getBoundingClientRect()
        setTooltip({
          visible: true,
          x: event.clientX - rect.left,
          y: event.clientY - rect.top,
          coin: d,
          pct,
        })
      })
      .on('mousemove', function(event: MouseEvent) {
        const rect = (svgRef.current as SVGSVGElement).getBoundingClientRect()
        setTooltip(prev => ({ ...prev, x: event.clientX - rect.left, y: event.clientY - rect.top }))
      })
      .on('mouseleave', function() {
        d3.select(this).select('.base')
          .attr('stroke-opacity', 0.6)
          .attr('stroke-width', (d: BubbleNode) => d.r > 35 ? 1.5 : 0.8)
        setTooltip(prev => ({ ...prev, visible: false }))
      })
  }

  function updateColors(
    svg: d3.Selection<SVGSVGElement, unknown, null, undefined>,
    coins: CoinPrice[],
    currentTf: Timeframe,
  ) {
    const coinMap = new Map(coins.map(c => [c.id, c]))

    svg.selectAll<SVGCircleElement, BubbleNode>('g.bubble circle.base')
      .transition().duration(450).ease(d3.easeQuadInOut)
      .attr('fill',   d => pctToColor(getPct(coinMap.get(d.id)!, currentTf)))
      .attr('stroke', d => pctToStroke(getPct(coinMap.get(d.id)!, currentTf)))

    svg.selectAll<SVGTextElement, BubbleNode>('g.bubble text.pct')
      .text(d => {
        const coin = coinMap.get(d.id)
        if (!coin) return ''
        const pct = getPct(coin, currentTf)
        return `${pct >= 0 ? '+' : ''}${pct.toFixed(2)}%`
      })
  }

  // ── Render ─────────────────────────────────────────────────────────────────

  return (
    <div className="glass rounded-xl overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-3.5 border-b border-border-dim">
        <div className="flex items-center gap-3">
          <p className="section-label">Market Bubble Chart</p>
          <span className="text-[10px] text-text-muted font-mono">
            {data ? `Top ${data.count} coins` : '—'}
          </span>
          {ready && (
            <span className="flex items-center gap-1 text-[10px] text-text-muted">
              <span className="live-dot" />
              <span className="font-mono">LIVE</span>
            </span>
          )}
        </div>

        {/* Timeframe tabs */}
        <div className="flex items-center bg-surface-2 rounded-lg p-0.5 gap-0.5">
          {TF_LABELS.map(({ key, label }) => (
            <button
              key={key}
              onClick={() => setTf(key)}
              className={`px-3 py-1 rounded-md text-xs font-mono font-medium transition-all duration-150 ${
                tf === key
                  ? 'bg-accent-cyan/15 text-accent-cyan border border-accent-cyan/30'
                  : 'text-text-muted hover:text-text-secondary'
              }`}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* Chart container */}
      <div className="relative" style={{ height: 540 }}>
        {/* Loading skeleton */}
        {isLoading && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="flex flex-col items-center gap-3">
              <div className="w-16 h-16 rounded-full border-2 border-accent-cyan/20 border-t-accent-cyan animate-spin" />
              <p className="text-text-muted text-xs font-mono">Loading market data…</p>
            </div>
          </div>
        )}

        {/* Error state */}
        {isError && (
          <div className="absolute inset-0 flex items-center justify-center">
            <p className="text-text-muted text-sm">Failed to load bubble data — check backend</p>
          </div>
        )}

        {/* D3 SVG */}
        {!isLoading && !isError && (
          <svg
            ref={svgRef}
            viewBox={`0 0 ${VW} ${VH}`}
            preserveAspectRatio="xMidYMid meet"
            style={{ width: '100%', height: '100%', display: 'block' }}
          />
        )}

        {/* Legend */}
        {ready && (
          <div className="absolute bottom-3 left-5 flex items-center gap-4">
            <div className="flex items-center gap-1.5">
              <div className="w-3 h-3 rounded-full" style={{ background: '#e02052' }} />
              <span className="text-[10px] text-text-muted font-mono">Loss</span>
            </div>
            <div className="flex items-center gap-1.5">
              <div className="w-3 h-3 rounded-full" style={{ background: '#1a2535' }} />
              <span className="text-[10px] text-text-muted font-mono">Neutral</span>
            </div>
            <div className="flex items-center gap-1.5">
              <div className="w-3 h-3 rounded-full" style={{ background: '#00cc66' }} />
              <span className="text-[10px] text-text-muted font-mono">Gain</span>
            </div>
            <span className="text-[10px] text-text-muted">· Size = Market Cap</span>
          </div>
        )}

        {/* Tooltip */}
        {tooltip.visible && tooltip.coin && (
          <div
            className="absolute z-20 pointer-events-none"
            style={{
              left: tooltip.x + 14,
              top:  tooltip.y - 10,
              transform: tooltip.x > VW * 0.6 ? 'translateX(-110%)' : undefined,
            }}
          >
            <div className="glass rounded-lg px-3.5 py-2.5 border border-white/15 shadow-card min-w-[170px]">
              {/* Coin header */}
              <div className="flex items-center gap-2 mb-2">
                <img
                  src={tooltip.coin.image}
                  alt={tooltip.coin.symbol}
                  className="w-5 h-5 rounded-full"
                  onError={e => { (e.target as HTMLImageElement).style.display = 'none' }}
                />
                <span className="text-text-primary text-sm font-semibold">{tooltip.coin.name}</span>
                <span className="text-text-muted text-xs font-mono">{tooltip.coin.symbol}</span>
              </div>
              {/* Stats */}
              <div className="space-y-1 text-xs">
                <div className="flex justify-between gap-4">
                  <span className="text-text-muted">Price</span>
                  <span className="text-text-primary font-mono">{fmtPrice(tooltip.coin.price)}</span>
                </div>
                <div className="flex justify-between gap-4">
                  <span className="text-text-muted">{tf.toUpperCase()} Change</span>
                  <span
                    className="font-mono font-semibold"
                    style={{ color: tooltip.pct >= 0 ? '#00ff88' : '#ff3366' }}
                  >
                    {tooltip.pct >= 0 ? '+' : ''}{tooltip.pct.toFixed(2)}%
                  </span>
                </div>
                <div className="flex justify-between gap-4">
                  <span className="text-text-muted">Market Cap</span>
                  <span className="text-text-secondary font-mono">{fmtMcap(tooltip.coin.marketCap)}</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
