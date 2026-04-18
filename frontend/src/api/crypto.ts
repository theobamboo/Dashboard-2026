import { useQuery } from '@tanstack/react-query'
import client from './client'

// ── Types ────────────────────────────────────────────────────────────────

export interface CoinPrice {
  id: string
  symbol: string
  name: string
  image: string
  current_price: number
  market_cap: number
  market_cap_rank: number
  total_volume: number
  high_24h: number | null
  low_24h: number | null
  price_change_24h: number | null
  price_change_percentage_1h: number | null
  price_change_percentage_24h: number | null
  price_change_percentage_7d: number | null
  circulating_supply: number | null
  ath: number | null
  ath_change_percentage: number | null
  last_updated: string | null
}

export interface PricesResponse {
  coins: CoinPrice[]
  count: number
  cached: boolean
  fetched_at: string
}

export interface DominanceResponse {
  btc_dominance: number
  eth_dominance: number
  total_market_cap_usd: number
  total_volume_24h_usd: number
  market_cap_change_24h_pct: number
  active_cryptocurrencies: number
  markets: number
  cached: boolean
  fetched_at: string
}

export interface FearGreedEntry {
  value: number
  classification: string
  timestamp: number
}

export interface FearGreedResponse {
  current: FearGreedEntry
  history: FearGreedEntry[]
  cached: boolean
  fetched_at: string
}

export interface CryptoOverview {
  market: string
  btc_dominance: number
  eth_dominance: number
  total_market_cap_usd: number
  market_cap_change_24h_pct: number
  fear_greed: { value: number; classification: string }
  fetched_at: string
}

// ── Fetch functions ───────────────────────────────────────────────────────

export const fetchCryptoOverview  = () => client.get<CryptoOverview>('/crypto/').then(r => r.data)
export const fetchPrices          = (top = 100) => client.get<PricesResponse>(`/crypto/prices?top=${top}`).then(r => r.data)
export const fetchDominance       = () => client.get<DominanceResponse>('/crypto/dominance').then(r => r.data)
export const fetchFearGreed       = (days = 7)  => client.get<FearGreedResponse>(`/crypto/fear-greed?days=${days}`).then(r => r.data)

// ── React Query hooks ────────────────────────────────────────────────────

export const useCryptoOverview = () =>
  useQuery({ queryKey: ['crypto', 'overview'], queryFn: fetchCryptoOverview, refetchInterval: 60_000, refetchIntervalInBackground: false })

export const usePrices = (top = 100) =>
  useQuery({ queryKey: ['crypto', 'prices', top], queryFn: () => fetchPrices(top), refetchInterval: 60_000, refetchIntervalInBackground: false })

export const useDominance = () =>
  useQuery({ queryKey: ['crypto', 'dominance'], queryFn: fetchDominance, refetchInterval: 300_000, refetchIntervalInBackground: false })

export const useFearGreed = (days = 7) =>
  useQuery({ queryKey: ['crypto', 'fear-greed', days], queryFn: () => fetchFearGreed(days), refetchInterval: 300_000, refetchIntervalInBackground: false })
