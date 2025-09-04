import { useState } from 'react'
import { DataTable, type DataTableColumn } from '@components/DataTable'
import HeaderInformation from '@components/HeaderInformation'
import { Button, Flex, Text, Badge, Dialog } from '@radix-ui/themes'
import { PlusIcon, Pencil1Icon, TrashIcon } from '@radix-ui/react-icons'
import { useRoles, useDeleteRole } from '@applications/queries/rbac'
import type { Role } from '@api/rbac'
import CreateRoleDialog from './CreateRoleDialog'
import EditRoleDialog from './EditRoleDialog'

export default function ListRoles() {
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [createDialogOpen, setCreateDialogOpen] = useState(false)
  const [editDialogOpen, setEditDialogOpen] = useState(false)
  const [selectedRole, setSelectedRole] = useState<Role | null>(null)

  const { data: roles = [], isLoading } = useRoles((page - 1) * pageSize, pageSize)
  const deleteRoleMutation = useDeleteRole()

  const handleEdit = (role: Role) => {
    setSelectedRole(role)
    setEditDialogOpen(true)
  }

  const handleDelete = async (role: Role) => {
    if (role.is_system) {
      alert('Cannot delete system roles')
      return
    }
    
    if (confirm(`Are you sure you want to delete role "${role.display_name}"?`)) {
      try {
        await deleteRoleMutation.mutateAsync(role.id)
      } catch (error) {
        console.error('Failed to delete role:', error)
      }
    }
  }

  const columns: Array<DataTableColumn<Role>> = [
    { key: 'id', header: 'ID', width: 80 },
    {
      key: 'name',
      header: 'Name',
      render: (row) => (
        <Flex direction="column" gap="1">
          <Text weight="medium">{row.display_name}</Text>
          <Text size="1" color="gray">{row.name}</Text>
        </Flex>
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
      key: 'is_system',
      header: 'Type',
      render: (row) => (
        <Badge color={row.is_system ? 'blue' : 'gray'}>
          {row.is_system ? 'System' : 'Custom'}
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
          {!row.is_system && (
            <Button
              size="1"
              variant="soft"
              color="red"
              onClick={() => handleDelete(row)}
            >
              <TrashIcon />
            </Button>
          )}
        </Flex>
      ),
    },
  ]

  return (
    <Flex direction="column" gap="4">
      <HeaderInformation
        breadcrumb={<Text as="span">Roles</Text>}
        title="Role Management"
        description="Manage user roles and their permissions"
        action={
          <Button onClick={() => setCreateDialogOpen(true)}>
            <PlusIcon />
            Create Role
          </Button>
        }
      />

      <DataTable
        data={roles}
        columns={columns}
        page={page}
        pageSize={pageSize}
        total={roles.length} // This should come from API
        onPageChange={setPage}
        onPageSizeChange={(size: number) => {
          setPageSize(size)
          setPage(1)
        }}
        loading={isLoading}
      />

      <CreateRoleDialog
        open={createDialogOpen}
        onOpenChange={setCreateDialogOpen}
      />

      <EditRoleDialog
        open={editDialogOpen}
        onOpenChange={setEditDialogOpen}
        role={selectedRole}
      />
    </Flex>
  )
}
