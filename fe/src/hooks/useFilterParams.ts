import { useState, useMemo, useCallback, useRef } from 'react'

export interface FilterState {
  [key: string]: any
}

export interface FilterConfig<T extends FilterState = FilterState> {
  initialFilters?: T
  debounceMs?: number
}

export function useFilterParams<T extends FilterState = FilterState>(
  config: FilterConfig<T> = {}
) {
  const {
    initialFilters = {} as T,
    debounceMs = 300
  } = config

  const [filters, setFilters] = useState<T>(initialFilters)
  const [debouncedFilters, setDebouncedFilters] = useState<T>(initialFilters)

  // Debounce filter changes
  const debounceTimeoutRef = useRef<NodeJS.Timeout | undefined>(undefined)

  const updateFilters = useCallback((newFilters: Partial<T>) => {
    setFilters(prev => ({ ...prev, ...newFilters }))
    
    // Clear existing timeout
    if (debounceTimeoutRef.current) {
      clearTimeout(debounceTimeoutRef.current)
    }

    // Set new timeout
    debounceTimeoutRef.current = setTimeout(() => {
      setDebouncedFilters(prev => ({ ...prev, ...newFilters }))
    }, debounceMs)
  }, [debounceMs])

  const setFilter = useCallback((key: keyof T, value: any) => {
    updateFilters({ [key]: value } as Partial<T>)
  }, [updateFilters])

  const removeFilter = useCallback((key: keyof T) => {
    const newFilters = { ...filters }
    delete newFilters[key]
    setFilters(newFilters)
    setDebouncedFilters(newFilters)
  }, [filters])

  const clearFilters = useCallback(() => {
    setFilters(initialFilters as T)
    setDebouncedFilters(initialFilters as T)
  }, [initialFilters])

  const hasActiveFilters = useMemo(() => {
    return Object.keys(filters).some(key => {
      const value = filters[key]
      return value !== undefined && value !== null && value !== ''
    })
  }, [filters])

  const activeFiltersCount = useMemo(() => {
    return Object.keys(filters).filter(key => {
      const value = filters[key]
      return value !== undefined && value !== null && value !== ''
    }).length
  }, [filters])

  return {
    filters,
    debouncedFilters,
    setFilter,
    removeFilter,
    clearFilters,
    updateFilters,
    hasActiveFilters,
    activeFiltersCount
  }
}

