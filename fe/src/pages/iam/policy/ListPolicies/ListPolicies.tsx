import { useState } from 'react'
import { DataTable, type DataTableColumn } from '@components/DataTable'
import HeaderInformation from '@components/HeaderInformation'
import { Button, Flex, Text, Badge } from '@radix-ui/themes'
import { PlusIcon, Pencil1Icon, TrashIcon, EyeOpenIcon } from '@radix-ui/react-icons'
import { usePolicies, useDeletePolicy } from '@applications/queries/abac'
import { useTableParams } from '@hooks'
import type { Policy } from '@api/abac'
import CreatePolicyDialog from './CreatePolicyDialog'
import EditPolicyDialog from './EditPolicyDialog'
import PolicyDetailsDialog from './PolicyDetailsDialog'


interface PolicyFilters {
  activeOnly?: boolean
}

export default function ListPolicies() {
  const { pagination } = useTableParams<PolicyFilters>({
    pagination: { defaultPage: 1, defaultPageSize: 10 }
  })

  const [createDialogOpen, setCreateDialogOpen] = useState(false)
  const [editDialogOpen, setEditDialogOpen] = useState(false)
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false)
  const [selectedPolicy, setSelectedPolicy] = useState<Policy | null>(null)

  const { data: policies = [], isLoading } = usePolicies(pagination.page, pagination.pageSize)
  const deletePolicyMutation = useDeletePolicy()

  const handleEdit = (policy: Policy) => {
    setSelectedPolicy(policy)
    setEditDialogOpen(true)
  }

  const handleView = (policy: Policy) => {
    setSelectedPolicy(policy)
    setDetailsDialogOpen(true)
  }

  const handleDelete = async (policy: Policy) => {
    if (confirm(`Are you sure you want to delete policy "${policy.name}"?`)) {
      try {
        await deletePolicyMutation.mutateAsync(policy.id)
      } catch (error) {
        console.error('Failed to delete policy:', error)
      }
    }
  }

  const columns: Array<DataTableColumn<Policy>> = [
    { key: 'id', header: 'ID', width: 80 },
    {
      key: 'name',
      header: 'Policy Name',
      render: (row) => (
        <Flex direction="column" gap="1">
          <Text weight="medium">{row.name}</Text>
          <Text size="1" color="gray">{row.policy_type}</Text>
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
      key: 'priority',
      header: 'Priority',
      render: (row) => (
        <Badge color="blue" variant="soft">
          {row.priority}
        </Badge>
      ),
    },
    {
      key: 'effect',
      header: 'Effect',
      render: (row) => (
        <Badge color={row.effect === 'allow' ? 'green' : 'red'}>
          {row.effect.toUpperCase()}
        </Badge>
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
            onClick={() => handleView(row)}
          >
            <EyeOpenIcon />
          </Button>
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

  return (
    <Flex direction="column" gap="4">
      <HeaderInformation
        breadcrumb={<Text as="span">Policies</Text>}
        title="Policy Management"
        description="Manage ABAC policies for attribute-based access control"
        action={
          <Button onClick={() => setCreateDialogOpen(true)}>
            <PlusIcon />
            Create Policy
          </Button>
        }
      />

      <DataTable<Policy>
        data={policies}
        columns={columns}
        page={pagination.page}
        pageSize={pagination.pageSize}
        total={policies.length} // This should come from API
        onPageChange={pagination.setPage}
        onPageSizeChange={pagination.setPageSize}
        loading={isLoading}
      />

      <CreatePolicyDialog
        open={createDialogOpen}
        onOpenChange={setCreateDialogOpen}
      />

      <EditPolicyDialog
        open={editDialogOpen}
        onOpenChange={setEditDialogOpen}
        policy={selectedPolicy}
      />

      <PolicyDetailsDialog
        open={detailsDialogOpen}
        onOpenChange={setDetailsDialogOpen}
        policy={selectedPolicy}
      />
    </Flex>
  )
}
