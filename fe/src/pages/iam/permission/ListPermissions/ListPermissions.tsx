import { useState } from 'react'
import { DataTable, type DataTableColumn } from '@components/DataTable'
import HeaderInformation from '@components/HeaderInformation'
import { Button, Flex, Text, Badge, Select } from '@radix-ui/themes'
import { PlusIcon, Pencil1Icon, TrashIcon } from '@radix-ui/react-icons'
import { usePermissions, useDeletePermission } from '@applications/queries/rbac'
import type { Permission } from '@api/rbac'
import CreatePermissionDialog from './CreatePermissionDialog'
import EditPermissionDialog from './EditPermissionDialog'

export default function ListPermissions() {
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [selectedResource, setSelectedResource] = useState<string>('all')
  const [createDialogOpen, setCreateDialogOpen] = useState(false)
  const [editDialogOpen, setEditDialogOpen] = useState(false)
  const [selectedPermission, setSelectedPermission] = useState<Permission | null>(null)

  const { data: permissions = [], isLoading } = usePermissions(
    page, 
    pageSize, 
    selectedResource === 'all' ? undefined : selectedResource
  )
  const deletePermissionMutation = useDeletePermission()

  const handleEdit = (permission: Permission) => {
    setSelectedPermission(permission)
    setEditDialogOpen(true)
  }

  const handleDelete = async (permission: Permission) => {
    if (confirm(`Are you sure you want to delete permission "${permission.display_name}"?`)) {
      try {
        await deletePermissionMutation.mutateAsync(permission.id)
      } catch (error) {
        console.error('Failed to delete permission:', error)
      }
    }
  }

  const columns: Array<DataTableColumn<Permission>> = [
    { key: 'id', header: 'ID', width: 80 },
    {
      key: 'name',
      header: 'Permission',
      render: (row) => (
        <Flex direction="column" gap="1">
          <Text weight="medium">{row.display_name}</Text>
          <Text size="1" color="gray">{row.name}</Text>
        </Flex>
      ),
    },
    {
      key: 'resource',
      header: 'Resource',
      render: (row) => (
        <Badge color="blue" variant="soft">
          {row.resource}
        </Badge>
      ),
    },
    {
      key: 'action',
      header: 'Action',
      render: (row) => (
        <Badge color="green" variant="soft">
          {row.action}
        </Badge>
      ),
    },
    {
      key: 'description',
      header: 'Description',
      render: (row) => (
        <Text size="2" color="gray" style={{ maxWidth: 300 }}>
          {row.description || 'No description'}
        </Text>
      ),
    },
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
      key: 'actions',
      header: 'Actions',
      render: (row) => (
        <Flex gap="2">
          <Button
            size="1"
            variant="soft"
            onClick={() => handleEdit(row)}
          >
            <Pencil1Icon />
          </Button>
          <Button
            size="1"
            variant="soft"
            color="red"
            onClick={() => handleDelete(row)}
          >
            <TrashIcon />
          </Button>
        </Flex>
      ),
    },
  ]

  const resourceOptions = [
    { value: 'all', label: 'All Resources' },
    { value: 'user', label: 'User' },
    { value: 'role', label: 'Role' },
    { value: 'permission', label: 'Permission' },
    { value: 'feature', label: 'Feature' },
    { value: 'policy', label: 'Policy' },
    { value: 'report', label: 'Report' },
  ]

  return (
    <Flex direction="column" gap="4">
      <HeaderInformation
        breadcrumb={<Text as="span">Permissions</Text>}
        title="Permission Management"
        description="Manage system permissions and access controls"
        action={
          <Button onClick={() => setCreateDialogOpen(true)}>
            <PlusIcon />
            Create Permission
          </Button>
        }
      />

      <Flex gap="4" align="center">
        <Text size="2" weight="medium">Filter by Resource:</Text>
        <Select.Root value={selectedResource} onValueChange={setSelectedResource}>
          <Select.Trigger placeholder="Select resource" />
          <Select.Content>
            {resourceOptions.map((option) => (
              <Select.Item key={option.value} value={option.value}>
                {option.label}
              </Select.Item>
            ))}
          </Select.Content>
        </Select.Root>
      </Flex>

      <DataTable
        data={permissions}
        columns={columns}
        page={page}
        pageSize={pageSize}
        total={permissions.length} // This should come from API
        onPageChange={setPage}
        onPageSizeChange={(size: number) => {
          setPageSize(size)
          setPage(1)
        }}
        loading={isLoading}
      />

      <CreatePermissionDialog
        open={createDialogOpen}
        onOpenChange={setCreateDialogOpen}
      />

      <EditPermissionDialog
        open={editDialogOpen}
        onOpenChange={setEditDialogOpen}
        permission={selectedPermission}
      />
    </Flex>
  )
}
