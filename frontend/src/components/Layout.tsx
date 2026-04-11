import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
import Header from './Header'

export default function Layout() {
  return (
    <div className="flex h-full bg-bg overflow-hidden">
      {/* Sidebar */}
      <Sidebar />

      {/* Main column */}
      <div className="flex flex-col flex-1 overflow-hidden">
        {/* Header */}
        <Header />

        {/* Page content */}
        <main className="flex-1 overflow-y-auto relative">
          {/* Subtle dot-grid bg */}
          <div className="dot-bg absolute inset-0 pointer-events-none opacity-30" />

          {/* Page */}
          <div className="relative z-10 p-6 page-enter">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}
