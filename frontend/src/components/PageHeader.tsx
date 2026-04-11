import type { ReactNode } from 'react'

interface PageHeaderProps {
  title: string
  subtitle?: string
  badge?: string
  badgeColor?: string
  actions?: ReactNode
}

export default function PageHeader({ title, subtitle, badge, badgeColor = '#00d4ff', actions }: PageHeaderProps) {
  return (
    <div className="flex items-start justify-between mb-6">
      <div>
        <div className="flex items-center gap-2.5 mb-1">
          <h1 className="text-xl font-bold text-text-primary tracking-tight">{title}</h1>
          {badge && (
            <span
              className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded-full border"
              style={{ color: badgeColor, borderColor: `${badgeColor}40`, background: `${badgeColor}12` }}
            >
              {badge}
            </span>
          )}
        </div>
        {subtitle && <p className="text-text-muted text-sm">{subtitle}</p>}
      </div>
      {actions && <div className="flex items-center gap-2">{actions}</div>}
    </div>
  )
}
