import { useState } from 'react'
import { Button, Flex, Text, TextField, Select } from '@radix-ui/themes'
import { useTableParams, useSearch } from '@hooks'

interface ExampleFilters {
  status?: string
  category?: string
}

export default function TableWithSearchExample() {
  const { pagination, filters } = useTableParams<ExampleFilters>({
    pagination: { defaultPage: 1, defaultPageSize: 10 },
    filters: { initialFilters: { status: 'all' } }
  })

  const search = useSearch({ debounceMs: 500, minLength: 2 })

  const [createDialogOpen, setCreateDialogOpen] = useState(false)

  // Example API call with all parameters
  // const { data, isLoading } = useQuery({
  //   queryKey: ['items', pagination.page, pagination.pageSize, filters.debouncedFilters, search.debouncedSearchTerm],
  //   queryFn: () => getItems({
  //     page: pagination.page,
  //     pageSize: pagination.pageSize,
  //     ...filters.debouncedFilters,
  //     search: search.isValidSearch ? search.debouncedSearchTerm : undefined
  //   })
  // })

  return (
    <Flex direction="column" gap="4">
      {/* Search */}
      <Flex gap="4" align="center">
        <TextField.Root
          placeholder="Search items..."
          value={search.searchTerm}
          onChange={(e) => search.setSearchTerm(e.target.value)}
        />
        {search.hasSearchTerm && (
          <Button variant="soft" onClick={search.clearSearch}>
            Clear
          </Button>
        )}
      </Flex>

      {/* Filters */}
      <Flex gap="4" align="center">
        <Text size="2" weight="medium">Status:</Text>
        <Select.Root
          value={filters.filters.status || 'all'}
          onValueChange={(value) => filters.setFilter('status', value)}
        >
          <Select.Trigger placeholder="Select status" />
          <Select.Content>
            <Select.Item value="all">All</Select.Item>
            <Select.Item value="active">Active</Select.Item>
            <Select.Item value="inactive">Inactive</Select.Item>
          </Select.Content>
        </Select.Root>

        <Text size="2" weight="medium">Category:</Text>
        <Select.Root
          value={filters.filters.category || 'all'}
          onValueChange={(value) => filters.setFilter('category', value)}
        >
          <Select.Trigger placeholder="Select category" />
          <Select.Content>
            <Select.Item value="all">All</Select.Item>
            <Select.Item value="tech">Tech</Select.Item>
            <Select.Item value="business">Business</Select.Item>
          </Select.Content>
        </Select.Root>

        {filters.hasActiveFilters && (
          <Button variant="soft" color="gray" onClick={filters.clearFilters}>
            Clear Filters ({filters.activeFiltersCount})
          </Button>
        )}
      </Flex>

      {/* Table would go here */}
      <Flex direction="column" gap="2">
        <Text>Current page: {pagination.page}</Text>
        <Text>Page size: {pagination.pageSize}</Text>
        <Text>Search term: {search.searchTerm}</Text>
        <Text>Debounced search: {search.debouncedSearchTerm}</Text>
        <Text>Filters: {JSON.stringify(filters.filters)}</Text>
        <Text>Debounced filters: {JSON.stringify(filters.debouncedFilters)}</Text>
      </Flex>

      {/* Pagination controls */}
      <Flex gap="2">
        <Button 
          onClick={() => pagination.setPage(pagination.page - 1)}
          disabled={pagination.page <= 1}
        >
          Previous
        </Button>
        <Button 
          onClick={() => pagination.setPage(pagination.page + 1)}
        >
          Next
        </Button>
        <Button onClick={pagination.resetPagination}>
          Reset Pagination
        </Button>
      </Flex>
    </Flex>
  )
}
