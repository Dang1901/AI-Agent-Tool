import { useState, useMemo } from 'react'

export interface PaginationState {
  page: number
  pageSize: number
}

export interface PaginationConfig {
  defaultPage?: number
  defaultPageSize?: number
  maxPageSize?: number
}

export function usePagination(config: PaginationConfig = {}) {
  const {
    defaultPage = 1,
    defaultPageSize = 10,
    maxPageSize = 100
  } = config

  const [page, setPage] = useState(defaultPage)
  const [pageSize, setPageSize] = useState(defaultPageSize)

  const paginationState: PaginationState = useMemo(() => ({
    page,
    pageSize: Math.min(pageSize, maxPageSize)
  }), [page, pageSize, maxPageSize])

  const handlePageChange = (newPage: number) => {
    setPage(Math.max(1, newPage))
  }

  const handlePageSizeChange = (newPageSize: number) => {
    const validPageSize = Math.min(Math.max(1, newPageSize), maxPageSize)
    setPageSize(validPageSize)
    setPage(1) // Reset to first page when page size changes
  }

  const resetPagination = () => {
    setPage(defaultPage)
    setPageSize(defaultPageSize)
  }

  return {
    ...paginationState,
    setPage: handlePageChange,
    setPageSize: handlePageSizeChange,
    resetPagination
  }
}