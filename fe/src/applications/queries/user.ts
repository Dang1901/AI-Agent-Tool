import { useQuery } from '@tanstack/react-query'
import { getUsers, type User } from '@api/user'

// User queries - Read only
export function useUsers(page = 1, pageSize = 100, search?: string, isActive?: boolean) {
  return useQuery({
    queryKey: ['users', page, pageSize, search, isActive],
    queryFn: () => getUsers(page, pageSize, search, isActive),
    // Auto-refresh every 30 seconds to sync new logged-in users
    refetchInterval: 30000,
    // Refetch when window regains focus
    refetchOnWindowFocus: true,
  })
}
