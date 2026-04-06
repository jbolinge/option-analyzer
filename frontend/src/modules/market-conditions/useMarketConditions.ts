import { useQuery } from '@tanstack/react-query'
import { fetchDashboard } from '../../api/client'

/**
 * TanStack Query hook for fetching the market conditions dashboard.
 *
 * staleTime: Infinity — data never auto-refetches. Use refetch() for
 * manual refresh triggered by the RefreshButton.
 */
export function useMarketConditions() {
  const query = useQuery({
    queryKey: ['market-conditions', 'dashboard'],
    queryFn: fetchDashboard,
    staleTime: Infinity,
  })

  return {
    data: query.data,
    isLoading: query.isLoading,
    isFetching: query.isFetching,
    isError: query.isError,
    error: query.error,
    refetch: query.refetch,
    dataUpdatedAt: query.dataUpdatedAt
      ? new Date(query.dataUpdatedAt)
      : null,
  }
}
