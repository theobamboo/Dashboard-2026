import { useQuery } from '@tanstack/react-query'
import client from './client'

export interface FxRate {
  price: number
  change_pct: number
}

export interface DxyStatus {
  price: number
  change_pct: number
}

export interface FxOverview {
  rates: Record<string, FxRate>
  dxy: DxyStatus | null
  cached: boolean
}

export const fxKeys = {
  overview: ['fx', 'overview'] as const,
}

export function useFxOverview() {
  return useQuery({
    queryKey: fxKeys.overview,
    queryFn: async () => {
      const res = await client.get<FxOverview>('/fx/overview')
      return res.data
    },
    refetchInterval: 60 * 1000,
    staleTime: 30 * 1000,
    refetchIntervalInBackground: false,
  })
}
