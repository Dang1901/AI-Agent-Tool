import { useState, useMemo, useCallback, useRef } from 'react'

export interface SearchConfig {
  debounceMs?: number
  minLength?: number
}

export function useSearch(config: SearchConfig = {}) {
  const {
    debounceMs = 300,
    minLength = 2
  } = config

  const [searchTerm, setSearchTerm] = useState('')
  const [debouncedSearchTerm, setDebouncedSearchTerm] = useState('')

  const debounceTimeoutRef = useRef<NodeJS.Timeout>()

  const updateSearch = useCallback((term: string) => {
    setSearchTerm(term)
    
    // Clear existing timeout
    if (debounceTimeoutRef.current) {
      clearTimeout(debounceTimeoutRef.current)
    }

    // Set new timeout
    debounceTimeoutRef.current = setTimeout(() => {
      setDebouncedSearchTerm(term)
    }, debounceMs)
  }, [debounceMs])

  const clearSearch = useCallback(() => {
    setSearchTerm('')
    setDebouncedSearchTerm('')
  }, [])

  const isValidSearch = useMemo(() => {
    return debouncedSearchTerm.length >= minLength
  }, [debouncedSearchTerm, minLength])

  const hasSearchTerm = useMemo(() => {
    return searchTerm.length > 0
  }, [searchTerm])

  return {
    searchTerm,
    debouncedSearchTerm,
    setSearchTerm: updateSearch,
    clearSearch,
    isValidSearch,
    hasSearchTerm
  }
}

