import { NavLink } from 'react-router-dom'
import { Bitcoin, BarChart2, Landmark, Globe2, ChevronLeft, ChevronRight } from 'lucide-react'
import { useState } from 'react'

const NAV = [
  { to: '/crypto',  icon: Bitcoin,    label: 'Crypto',     accent: '#00d4ff' },
  { to: '/stocks',  icon: BarChart2,  label: 'Stocks / ETFs', accent: '#7c3aed' },
  { to: '/bonds',   icon: Landmark,   label: 'Bonds / Macro', accent: '#f0a500' },
  { to: '/fx',      icon: Globe2,     label: 'FX',         accent: '#00ff88' },
]

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false)

  return (
    <aside
      className="relative flex flex-col border-r border-border-dim bg-surface transition-all duration-300 ease-in-out flex-shrink-0"
      style={{ width: collapsed ? 60 : 220 }}
    >
      {/* Logo */}
      <div className="h-14 flex items-center px-4 border-b border-border-dim overflow-hidden">
        <div className="flex items-center gap-2.5 min-w-0">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-accent-cyan to-accent-blue flex-shrink-0 flex items-center justify-center shadow-glow-cyan">
            <span className="text-bg text-xs font-black">LTD</span>
          </div>
          {!collapsed && (
            <div className="overflow-hidden">
              <p className="text-text-primary text-xs font-bold leading-tight truncate">Living the Dream</p>
              <p className="text-text-muted text-[10px] leading-tight">Trading Dashboard</p>
            </div>
          )}
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-4 overflow-hidden">
        {!collapsed && (
          <p className="section-label px-4 mb-2">Markets</p>
        )}
        <ul className="space-y-0.5 px-2">
          {NAV.map(({ to, icon: Icon, label, accent }) => (
            <li key={to}>
              <NavLink
                to={to}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150 group relative overflow-hidden ${
                    isActive
                      ? 'text-text-primary bg-white/[0.07] border border-white/[0.10]'
                      : 'text-text-secondary hover:text-text-primary hover:bg-white/[0.04]'
                  }`
                }
                title={collapsed ? label : undefined}
              >
                {({ isActive }) => (
                  <>
                    {/* Active left-border glow */}
                    {isActive && (
                      <span
                        className="absolute left-0 top-2 bottom-2 w-0.5 rounded-r"
                        style={{ background: accent, boxShadow: `0 0 8px ${accent}` }}
                      />
                    )}
                    <Icon
                      size={16}
                      className="flex-shrink-0 transition-colors duration-150"
                      style={{ color: isActive ? accent : undefined }}
                    />
                    {!collapsed && (
                      <span className="truncate">{label}</span>
                    )}
                    {isActive && !collapsed && (
                      <span
                        className="ml-auto w-1.5 h-1.5 rounded-full flex-shrink-0"
                        style={{ background: accent, boxShadow: `0 0 6px ${accent}` }}
                      />
                    )}
                  </>
                )}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>

      {/* Collapse toggle */}
      <button
        onClick={() => setCollapsed(c => !c)}
        className="h-10 flex items-center justify-center border-t border-border-dim text-text-muted hover:text-accent-cyan transition-colors duration-150"
        title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
      >
        {collapsed ? <ChevronRight size={14} /> : <ChevronLeft size={14} />}
      </button>
    </aside>
  )
}
