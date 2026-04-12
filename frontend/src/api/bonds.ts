import { useQuery } from '@tanstack/react-query'
import client from './client'

export interface MacroStatus {
  value: number
  change: number
}

export interface DxyStatus {
  price: number
  change_pct: number
}

export interface BondsOverview {
  macro: Record<string, MacroStatus>
  dxy: DxyStatus | null
  cached: boolean
}

export const bondsKeys = {
  overview: ['bonds', 'overview'] as const,
}

export function useBondsOverview() {
  return useQuery({
    queryKey: bondsKeys.overview,
    queryFn: async () => {
      const res = await client.get<BondsOverview>('/bonds/overview')
      return res.data
    },
    // Refetch every 5 minutes
    refetchInterval: 5 * 60 * 1000,
    staleTime: 60 * 1000,
  })
}
