import { useEffect, useState } from 'react'
import { Activity } from 'lucide-react'
import TickerStrip from './TickerStrip'

function UtcClock() {
  const [time, setTime] = useState(() => new Date())
  useEffect(() => {
    const id = setInterval(() => setTime(new Date()), 1000)
    return () => clearInterval(id)
  }, [])
  return (
    <span className="font-mono text-xs text-text-muted tabular-nums">
      {time.toUTCString().slice(17, 25)}{' '}
      <span className="text-text-muted/50">UTC</span>
    </span>
  )
}

export default function Header() {
  return (
    <header className="h-14 flex items-center border-b border-border-dim bg-surface flex-shrink-0 overflow-hidden">
      {/* Live indicator */}
      <div className="flex items-center gap-2 px-4 border-r border-border-dim h-full flex-shrink-0">
        <span className="live-dot" />
        <Activity size={13} className="text-text-muted" />
        <span className="text-[10px] font-mono text-text-muted uppercase tracking-wider hidden sm:block">Live</span>
      </div>

      {/* Scrolling ticker */}
      <TickerStrip />

      {/* Clock */}
      <div className="flex items-center gap-3 px-4 border-l border-border-dim h-full flex-shrink-0">
        <UtcClock />
      </div>
    </header>
  )
}
