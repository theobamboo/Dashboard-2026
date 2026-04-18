import { useQuery } from '@tanstack/react-query'
import client from './client'

export interface AssetStatus {
  price: number
  change_pct: number
}

export interface StocksOverview {
  assets: Record<string, AssetStatus>
  cached: boolean
}

export const stocksKeys = {
  overview: ['stocks', 'overview'] as const,
}

export function useStocksOverview() {
  return useQuery({
    queryKey: stocksKeys.overview,
    queryFn: async () => {
      const res = await client.get<StocksOverview>('/stocks/overview')
      return res.data
    },
    // Refetch every 60 seconds since we cache on backend for 60s
    refetchInterval: 60 * 1000,
    staleTime: 30 * 1000,
    refetchIntervalInBackground: false,
  })
}
