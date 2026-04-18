import { useEffect, useRef, memo, useId } from 'react'

interface TradingViewChartProps {
  symbol: string
  height?: number
  theme?: 'dark' | 'light'
  interval?: string
  /** Optional label shown above the chart */
  label?: string
}

/**
 * Embeds the TradingView Advanced Chart widget via the free script embed.
 * No API key required — uses the public widget endpoint.
 *
 * Key implementation notes:
 * - Uses textContent (not innerHTML) to set the JSON config on the script tag,
 *   which is the browser-compatible way to pass config to dynamically loaded scripts.
 * - Each instance gets a unique DOM id (via useId) so multiple charts on the
 *   same page don't collide.
 * - The container is fully cleared and re-built when `symbol` changes.
 */
const TradingViewChart = memo(function TradingViewChart({
  symbol,
  height = 400,
  theme = 'dark',
  interval = 'D',
  label,
}: TradingViewChartProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  // Stable unique id for this chart instance (React 18+)
  const uid = useId().replace(/:/g, '')

  useEffect(() => {
    const container = containerRef.current
    if (!container) return

    // ── Tear down any previous widget ──────────────────────────────────────
    container.innerHTML = ''

    // ── Build the widget structure TradingView expects ─────────────────────
    //   <div class="tradingview-widget-container">        ← our ref
    //     <div class="tradingview-widget-container__widget" id="tv-{uid}">
    //     <script type="text/javascript">{ config JSON }</script>
    //   </div>

    const widgetDiv = document.createElement('div')
    widgetDiv.className = 'tradingview-widget-container__widget'
    widgetDiv.id = `tv-widget-${uid}`
    widgetDiv.style.height = '100%'
    widgetDiv.style.width = '100%'
    container.appendChild(widgetDiv)

    const config = {
      autosize: true,
      symbol,
      interval,
      timezone: 'Etc/UTC',
      theme,
      style: '1', // candlestick
      locale: 'en',
      enable_publishing: false,
      backgroundColor: 'rgba(10, 16, 28, 0)',
      gridColor: 'rgba(255, 255, 255, 0.04)',
      hide_top_toolbar: false,
      hide_legend: false,
      save_image: false,
      calendar: false,
      hide_volume: false,
      container_id: `tv-widget-${uid}`,
      support_host: 'https://www.tradingview.com',
    }

    const script = document.createElement('script')
    script.type = 'text/javascript'
    script.src = 'https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js'
    script.async = true
    // textContent is the correct way to pass inline config to a dynamically
    // created external script — innerHTML can be blocked by CSP / sanitisers.
    script.textContent = JSON.stringify(config)

    container.appendChild(script)

    return () => {
      container.innerHTML = ''
    }
  }, [symbol, theme, interval, uid])

  return (
    <div className="glass rounded-xl overflow-hidden">
      {label && (
        <div className="px-5 py-3.5 border-b border-border-dim flex items-center justify-between">
          <p className="section-label">{label}</p>
          <span className="text-[10px] font-mono text-text-muted px-2 py-0.5 rounded border border-border-dim">
            {symbol}
          </span>
        </div>
      )}
      {/* Fixed-height wrapper — required for autosize to work correctly */}
      <div style={{ height: `${height}px`, position: 'relative' }}>
        <div
          ref={containerRef}
          className="tradingview-widget-container"
          style={{ height: '100%', width: '100%' }}
        />
      </div>
      {/* TradingView mandatory attribution */}
      <div className="px-4 py-1.5 border-t border-border-dim">
        <a
          href="https://www.tradingview.com/"
          target="_blank"
          rel="noopener noreferrer"
          className="text-[10px] text-text-muted/50 hover:text-text-muted transition-colors"
        >
          Powered by TradingView
        </a>
      </div>
    </div>
  )
})

export default TradingViewChart
