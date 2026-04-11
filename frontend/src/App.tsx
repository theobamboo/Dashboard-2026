import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import Layout from './components/Layout'
import CryptoPage from './pages/CryptoPage'
import StocksPage from './pages/StocksPage'
import BondsPage from './pages/BondsPage'
import FXPage from './pages/FXPage'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,       // consider data fresh for 30s
      retry: 2,
      refetchOnWindowFocus: false,
    },
  },
})

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route index element={<Navigate to="/crypto" replace />} />
            <Route path="crypto"  element={<CryptoPage />} />
            <Route path="stocks"  element={<StocksPage />} />
            <Route path="bonds"   element={<BondsPage />} />
            <Route path="fx"      element={<FXPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}
