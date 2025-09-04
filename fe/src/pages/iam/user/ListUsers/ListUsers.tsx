import { useState } from 'react'
import { DataTable, type DataTableColumn } from '@components/DataTable'
import HeaderInformation from '@components/HeaderInformation'
import { Button, Flex, Text, Badge, TextField, Select } from '@radix-ui/themes'
import { EyeOpenIcon, ReloadIcon } from '@radix-ui/react-icons'
import { useUsers } from '@applications/queries/user'
import { useTableParams, useSearch } from '@hooks'
import type { User } from '@api/user'
import UserDetailsDialog from './UserDetailsDialog'

interface UserFilters {
  isActive?: boolean
}

export default function ListUsers() {
  const { pagination, filters } = useTableParams<UserFilters>({
    pagination: { defaultPage: 1, defaultPageSize: 10 },
    filters: { initialFilters: { isActive: undefined } }
  })

  const search = useSearch({ debounceMs: 500, minLength: 2 })

  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false)
  const [selectedUser, setSelectedUser] = useState<User | null>(null)

  const { data: users = [], isLoading, refetch } = useUsers(
    pagination.page, 
    pagination.pageSize, 
    search.isValidSearch ? search.debouncedSearchTerm : undefined,
    filters.debouncedFilters.isActive
  )

  const handleView = (user: User) => {
    setSelectedUser(user)
    setDetailsDialogOpen(true)
  }

  const handleRefresh = () => {
    refetch()
  }

  const columns: Array<DataTableColumn<User>> = [
    { key: 'id', header: 'ID', width: 80 },
    {
      key: 'user',
      header: 'User',
      render: (row) => (
        <Flex direction="column" gap="1">
          <Text weight="medium">{row.name || 'No name'}</Text>
          <Text size="1" color="gray">{row.email}</Text>
        </Flex>
      ),
    },
    // {
    //   key: 'department',
    //   header: 'Department',
    //   render: (row) => (
    //     <Text size="2">{row.department || 'N/A'}</Text>
    //   ),
    // },
    // {
    //   key: 'position',
    //   header: 'Position',
    //   render: (row) => (
    //     <Text size="2">{row.position || 'N/A'}</Text>
    //   ),
    // },
    // {
    //   key: 'clearance_level',
    //   header: 'Clearance',
    //   render: (row) => (
    //     <Badge color="blue" variant="soft">
    //       {row.clearance_level || 'N/A'}
    //     </Badge>
    //   ),
    // },
    {
      key: 'is_active',
      header: 'Status',
      render: (row) => (
        <Badge color={row.is_active ? 'green' : 'red'}>
          {row.is_active ? 'Active' : 'Inactive'}
        </Badge>
      ),
    },
    {
      key: 'is_verified',
      header: 'Verified',
      render: (row) => (
        <Badge color={row.is_verified ? 'green' : 'orange'}>
          {row.is_verified ? 'Verified' : 'Pending'}
        </Badge>
      ),
    },
    {
      key: 'created_at',
      header: 'Registered',
      render: (row) => (
        <Text size="1" color="gray">
          {new Date(row.created_at).toLocaleString()}
        </Text>
      ),
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (row) => (
        <Flex gap="2">
          <Button
            size="1"
            variant="soft"
            onClick={() => handleView(row)}
          >
            <EyeOpenIcon />
          </Button>
        </Flex>
      ),
    },
  ]

  const statusOptions = [
    { value: 'all', label: 'All Status' },
    { value: 'active', label: 'Active' },
    { value: 'inactive', label: 'Inactive' },
  ]

  return (
    <Flex direction="column" gap="4">
      <HeaderInformation
        breadcrumb={<Text as="span">Users</Text>}
        title="User Management"
        description="View all registered users in the system (auto-sync every 30s)"
        action={
          <Button onClick={handleRefresh} disabled={isLoading}>
            <ReloadIcon />
            Refresh
          </Button>
        }
      />

      {/* Search */}
      <Flex gap="4" align="center">
        <TextField.Root
          placeholder="Search users by name, email, or phone..."
          value={search.searchTerm}
          onChange={(e) => search.setSearchTerm(e.target.value)}
          style={{ minWidth: 300 }}
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
          value={filters.filters.isActive === undefined ? 'all' : 
                 filters.filters.isActive ? 'active' : 'inactive'}
          onValueChange={(value) => {
            if (value === 'all') {
              filters.setFilter('isActive', undefined)
            } else {
              filters.setFilter('isActive', value === 'active')
            }
          }}
        >
          <Select.Trigger placeholder="Select status" />
          <Select.Content>
            {statusOptions.map((option) => (
              <Select.Item key={option.value} value={option.value}>
                {option.label}
              </Select.Item>
            ))}
          </Select.Content>
        </Select.Root>

        {filters.hasActiveFilters && (
          <Button 
            variant="soft" 
            color="gray" 
            onClick={filters.clearFilters}
          >
            Clear Filters ({filters.activeFiltersCount})
          </Button>
        )}
      </Flex>

      <DataTable
        data={users}
        columns={columns}
        page={pagination.page}
        pageSize={pagination.pageSize}
        total={users.length} // This should come from API
        onPageChange={pagination.setPage}
        onPageSizeChange={pagination.setPageSize}
        loading={isLoading}
      />

      <UserDetailsDialog
        open={detailsDialogOpen}
        onOpenChange={setDetailsDialogOpen}
        user={selectedUser}
      />
    </Flex>
  )
}
