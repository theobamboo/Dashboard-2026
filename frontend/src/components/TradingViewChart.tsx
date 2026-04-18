import { useEffect, useRef, memo } from 'react'

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
 * The container div is cleared and re-populated whenever `symbol` changes.
 */
const TradingViewChart = memo(function TradingViewChart({
  symbol,
  height = 400,
  theme = 'dark',
  interval = 'D',
  label,
}: TradingViewChartProps) {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const container = containerRef.current
    if (!container) return

    // TradingView requires a fresh DOM node each time — clear previous widget
    container.innerHTML = ''

    // Inner wrapper that TV targets
    const widgetWrapper = document.createElement('div')
    widgetWrapper.className = 'tradingview-widget-container__widget'
    container.appendChild(widgetWrapper)

    const script = document.createElement('script')
    script.type = 'text/javascript'
    script.src = 'https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js'
    script.async = true
    script.innerHTML = JSON.stringify({
      autosize: true,
      symbol,
      interval,
      timezone: 'Etc/UTC',
      theme,
      style: '1',
      locale: 'en',
      enable_publishing: false,
      backgroundColor: 'rgba(10, 16, 28, 0)',
      gridColor: 'rgba(255, 255, 255, 0.04)',
      hide_top_toolbar: false,
      hide_legend: false,
      save_image: false,
      calendar: false,
      hide_volume: false,
      support_host: 'https://www.tradingview.com',
    })

    container.appendChild(script)

    return () => {
      container.innerHTML = ''
    }
  }, [symbol, theme, interval])

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
      {/* The fixed height wrapper keeps autosize working correctly */}
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
