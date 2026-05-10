import { TrendingUp, TrendingDown, Minus } from 'lucide-react'
import type { ReactNode } from 'react'

type Variant = 'gain' | 'loss' | 'neutral' | 'default'

interface StatCardProps {
  label: string
  value: string | number
  subValue?: string
  change?: number | null       // percentage — drives variant if set
  variant?: Variant
  icon?: ReactNode
  suffix?: string
  loading?: boolean
}

function getVariant(change?: number | null, variant?: Variant): Variant {
  if (variant && variant !== 'default') return variant
  if (change == null) return 'default'
  if (change > 0) return 'gain'
  if (change < 0) return 'loss'
  return 'neutral'
}

const VARIANT_STYLES: Record<Variant, string> = {
  gain:    'border-gain/20 shadow-glow-gain/5',
  loss:    'border-loss/20 shadow-glow-loss/5',
  neutral: 'border-neutral/20',
  default: 'border-border-dim',
}

const CHANGE_STYLES: Record<Variant, string> = {
  gain:    'text-gain',
  loss:    'text-loss',
  neutral: 'text-neutral',
  default: 'text-text-muted',
}

export default function StatCard({
  label, value, subValue, change, variant, icon, suffix, loading = false,
}: StatCardProps) {
  const v = getVariant(change, variant)

  if (loading) {
    return (
      <div className="glass rounded-xl p-4 animate-pulse">
        <div className="h-3 w-20 bg-surface-2 rounded mb-3" />
        <div className="h-7 w-28 bg-surface-2 rounded mb-2" />
        <div className="h-3 w-16 bg-surface-2 rounded" />
      </div>
    )
  }

  return (
    <div className={`glass rounded-xl p-4 transition-all duration-200 hover:border-white/[0.15] border ${VARIANT_STYLES[v]}`}>
      {/* Label row */}
      <div className="flex items-center justify-between mb-1.5">
        <span className="section-label">{label}</span>
        {icon && <span className="text-text-muted">{icon}</span>}
      </div>

      {/* Main value */}
      <p className="font-mono text-[1.4rem] font-bold text-text-primary leading-tight tracking-tight tabular-nums">
        {typeof value === 'number' ? value.toLocaleString('en-US', { maximumFractionDigits: 2 }) : value}
        {suffix && <span className="text-sm text-text-muted font-normal ml-1">{suffix}</span>}
      </p>

      {/* Bottom row — sub value or change badge */}
      <div className="flex items-center gap-2 mt-1.5">
        {change != null && (
          <span className={`inline-flex items-center gap-0.5 text-xs font-mono font-medium ${CHANGE_STYLES[v]}`}>
            {change > 0 ? <TrendingUp size={10} /> : change < 0 ? <TrendingDown size={10} /> : <Minus size={10} />}
            {change > 0 ? '+' : ''}{change.toFixed(2)}%
          </span>
        )}
        {subValue && <span className="text-text-muted text-xs">{subValue}</span>}
      </div>
    </div>
  )
}
