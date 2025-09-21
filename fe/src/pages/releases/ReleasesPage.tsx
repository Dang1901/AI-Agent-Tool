import React, { useState } from 'react'
import { 
  Box, 
  Button, 
  Card, 
  Flex, 
  Heading, 
  Text, 
  TextField, 
  Select, 
  Badge,
  Table,
  Dialog,
  TextArea,
  Separator
} from '@radix-ui/themes'
import { PlusIcon, EyeOpenIcon, CheckIcon } from '@radix-ui/react-icons'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { releaseApi } from '../../services/api'
import { useToastNotification } from '../../hooks/useToastNotification'
import { WarningConfirmDialog } from '../../components/ConfirmDialog'

interface Release {
  id: string
  service_id: string
  environment: string
  title: string
  description?: string
  status: string
  changes: ReleaseChange[]
  created_by: string
  created_at: string
  applied_by?: string
  applied_at?: string
}

interface ReleaseChange {
  env_var_id: string
  action: string
  old_value?: string
  new_value?: string
}

interface CreateReleaseData {
  service_id: string
  environment: string
  title: string
  description?: string
  changes: ReleaseChange[]
  created_by: string
}

// interface ReleaseStatus {
//   release: Release
//   approvals: any[]
//   can_be_approved: boolean
//   can_be_applied: boolean
//   can_be_cancelled: boolean
// }

const ReleasesPage: React.FC = () => {
  const [filters, setFilters] = useState({
    service_id: '',
    environment: '',
    status: 'all'
  })
  const [page, setPage] = useState(1)
  
  const toast = useToastNotification()
  const [size] = useState(50)
  const [showCreateDialog, setShowCreateDialog] = useState(false)
  const [showReleaseDetail, setShowReleaseDetail] = useState(false)
  const [showApproveDialog, setShowApproveDialog] = useState(false)
  const [showApplyDialog, setShowApplyDialog] = useState(false)
  const [selectedRelease, setSelectedRelease] = useState<Release | null>(null)

  const queryClient = useQueryClient()

  // Fetch releases
  const { data: releases, isLoading, error } = useQuery<Release[]>({
    queryKey: ['releases', filters, page, size],
    queryFn: () => {
      // Convert "all" values to empty strings for API
      const apiFilters = {
        ...filters,
        status: filters.status === 'all' ? '' : filters.status,
        page,
        size
      }
      return releaseApi.listReleases(apiFilters)
    }
  })

  // Create release mutation
  const createMutation = useMutation({
    mutationFn: releaseApi.createRelease,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['releases'] })
      setShowCreateDialog(false)
      toast.showCreateSuccess('Release')
    },
    onError: (error: any) => {
      toast.showCreateError('Release', error?.response?.data?.detail || error.message)
    }
  })

  // Approve release mutation
  const approveMutation = useMutation({
    mutationFn: ({ id, approver_id, comment }: { id: string, approver_id: string, comment?: string }) => 
      releaseApi.approveRelease(id, approver_id, comment),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['releases'] })
      toast.showApiSuccess('Release approved successfully')
    },
    onError: (error: any) => {
      toast.showApiError('Failed to approve release', error?.response?.data?.detail || error.message)
    }
  })

  // Apply release mutation
  const applyMutation = useMutation({
    mutationFn: ({ id, applied_by }: { id: string, applied_by: string }) => 
      releaseApi.applyRelease(id, applied_by),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['releases'] })
      toast.showApiSuccess('Release applied successfully')
    },
    onError: (error: any) => {
      toast.showApiError('Failed to apply release', error?.response?.data?.detail || error.message)
    }
  })

  const handleFilterChange = (key: string, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }))
    setPage(1)
  }

  const handleCreateRelease = (data: CreateReleaseData) => {
    createMutation.mutate(data)
  }

  const handleApproveRelease = (release: Release) => {
    setSelectedRelease(release)
    setShowApproveDialog(true)
  }

  const handleApplyRelease = (release: Release) => {
    setSelectedRelease(release)
    setShowApplyDialog(true)
  }

  const confirmApproveRelease = () => {
    if (selectedRelease) {
      approveMutation.mutate({ 
        id: selectedRelease.id, 
        approver_id: 'current_user', 
        comment: 'Approved via UI' 
      })
    }
  }

  const confirmApplyRelease = () => {
    if (selectedRelease) {
      applyMutation.mutate({ 
        id: selectedRelease.id, 
        applied_by: 'current_user' 
      })
    }
  }

  const handleViewRelease = (release: Release) => {
    setSelectedRelease(release)
    setShowReleaseDetail(true)
  }

  if (isLoading) return <div>Loading...</div>
  if (error) return <div>Error: {error.message}</div>

  return (
    <Box p="4">
      <Flex justify="between" align="center" mb="4">
        <Heading size="8">Releases</Heading>
        <Button onClick={() => setShowCreateDialog(true)}>
          <PlusIcon />
          Create Release
        </Button>
      </Flex>

      {/* Filters */}
      <Card mb="4" style={{ padding: '12px' }}>
        <Flex gap="3" wrap="wrap">
          <TextField.Root
            placeholder="Service ID"
            value={filters.service_id}
            onChange={(e) => handleFilterChange('service_id', e.target.value)}
          />

          <TextField.Root
            placeholder="Environment"
            value={filters.environment}
            onChange={(e) => handleFilterChange('environment', e.target.value)}
          />

          <Select.Root
            value={filters.status}
            onValueChange={(value) => handleFilterChange('status', value)}
          >
            <Select.Trigger placeholder="Status" />
            <Select.Content>
              <Select.Item value="all">All</Select.Item>
              <Select.Item value="DRAFT">Draft</Select.Item>
              <Select.Item value="PENDING_APPROVAL">Pending Approval</Select.Item>
              <Select.Item value="APPROVED">Approved</Select.Item>
              <Select.Item value="APPLIED">Applied</Select.Item>
              <Select.Item value="REJECTED">Rejected</Select.Item>
              <Select.Item value="CANCELLED">Cancelled</Select.Item>
            </Select.Content>
          </Select.Root>
        </Flex>
      </Card>

      {/* Releases Table */}
      <Card>
        <Table.Root>
          <Table.Header>
            <Table.Row>
              <Table.ColumnHeaderCell>Title</Table.ColumnHeaderCell>
              <Table.ColumnHeaderCell>Service</Table.ColumnHeaderCell>
              <Table.ColumnHeaderCell>Environment</Table.ColumnHeaderCell>
              <Table.ColumnHeaderCell>Status</Table.ColumnHeaderCell>
              <Table.ColumnHeaderCell>Created By</Table.ColumnHeaderCell>
              <Table.ColumnHeaderCell>Created At</Table.ColumnHeaderCell>
              <Table.ColumnHeaderCell>Actions</Table.ColumnHeaderCell>
            </Table.Row>
          </Table.Header>
          <Table.Body>
            {releases?.map((release) => (
              <Table.Row key={release.id}>
                <Table.Cell>
                  <Text weight="medium">{release.title}</Text>
                </Table.Cell>
                <Table.Cell>
                  <Text>{release.service_id}</Text>
                </Table.Cell>
                <Table.Cell>
                  <Text>{release.environment}</Text>
                </Table.Cell>
                <Table.Cell>
                  <Badge 
                    color={getStatusColor(release.status)}
                    variant="soft"
                  >
                    {release.status}
                  </Badge>
                </Table.Cell>
                <Table.Cell>
                  <Text size="2">{release.created_by}</Text>
                </Table.Cell>
                <Table.Cell>
                  <Text size="2">
                    {new Date(release.created_at).toLocaleDateString()}
                  </Text>
                </Table.Cell>
                <Table.Cell>
                  <Flex gap="1">
                    <Button
                      size="1"
                      variant="outline"
                      onClick={() => handleViewRelease(release)}
                    >
                      <EyeOpenIcon />
                      View
                    </Button>
                    {release.status === 'PENDING_APPROVAL' && (
                      <Button
                        size="1"
                        variant="outline"
                        color="green"
                        onClick={() => handleApproveRelease(release)}
                      >
                        <CheckIcon />
                        Approve
                      </Button>
                    )}
                    {release.status === 'APPROVED' && (
                      <Button
                        size="1"
                        variant="outline"
                        color="blue"
                        onClick={() => handleApplyRelease(release)}
                      >
                        Apply
                      </Button>
                    )}
                  </Flex>
                </Table.Cell>
              </Table.Row>
            ))}
          </Table.Body>
        </Table.Root>
      </Card>

      {/* Create Release Dialog */}
      <Dialog.Root open={showCreateDialog} onOpenChange={setShowCreateDialog}>
        <Dialog.Content>
          <Dialog.Title>Create Release</Dialog.Title>
          <Dialog.Description>
            Create a new release with environment variable changes
          </Dialog.Description>
          
          <Box mt="4">
            <CreateReleaseForm onSubmit={handleCreateRelease} />
          </Box>
        </Dialog.Content>
      </Dialog.Root>

      {/* Release Detail Dialog */}
      <Dialog.Root open={showReleaseDetail} onOpenChange={setShowReleaseDetail}>
        <Dialog.Content>
          <Dialog.Title>Release Details</Dialog.Title>
          <Dialog.Description>
            {selectedRelease?.title}
          </Dialog.Description>
          
          <Box mt="4">
            <ReleaseDetail release={selectedRelease} />
          </Box>
        </Dialog.Content>
      </Dialog.Root>

      {/* Approve Confirmation Dialog */}
      <WarningConfirmDialog
        open={showApproveDialog}
        onOpenChange={setShowApproveDialog}
        title="Approve Release"
        description={`Are you sure you want to approve release "${selectedRelease?.title}"? This will make it ready for deployment.`}
        onConfirm={confirmApproveRelease}
        loading={approveMutation.isPending}
      />

      {/* Apply Confirmation Dialog */}
      <WarningConfirmDialog
        open={showApplyDialog}
        onOpenChange={setShowApplyDialog}
        title="Apply Release"
        description={`Are you sure you want to apply release "${selectedRelease?.title}"? This will deploy the changes to the environment.`}
        onConfirm={confirmApplyRelease}
        loading={applyMutation.isPending}
      />
    </Box>
  )
}

// Helper function to get status color
const getStatusColor = (status: string) => {
  switch (status) {
    case 'DRAFT': return 'gray'
    case 'PENDING_APPROVAL': return 'orange'
    case 'APPROVED': return 'green'
    case 'APPLIED': return 'blue'
    case 'REJECTED': return 'red'
    case 'CANCELLED': return 'gray'
    default: return 'gray'
  }
}

// Create Release Form Component
const CreateReleaseForm: React.FC<{ onSubmit: (data: CreateReleaseData) => void }> = ({ onSubmit }) => {
  const [formData, setFormData] = useState({
    service_id: '',
    environment: '',
    title: '',
    description: '',
    changes: [],
    created_by: 'current_user'
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit(formData)
  }

  return (
    <form onSubmit={handleSubmit}>
      <Flex direction="column" gap="3">
        <Box>
          <Text size="2" weight="medium" mb="1" style={{ display: 'block' }}>
            Service ID *
          </Text>
          <TextField.Root
            placeholder="payment-service, user-api, etc."
            value={formData.service_id}
            onChange={(e) => setFormData(prev => ({ ...prev, service_id: e.target.value }))}
            required
          />
        </Box>
        
        <Box>
          <Text size="2" weight="medium" mb="1" style={{ display: 'block' }}>
            Environment *
          </Text>
          <TextField.Root
            placeholder="production, staging, development"
            value={formData.environment}
            onChange={(e) => setFormData(prev => ({ ...prev, environment: e.target.value }))}
            required
          />
        </Box>
        
        <Box>
          <Text size="2" weight="medium" mb="1" style={{ display: 'block' }}>
            Release Title *
          </Text>
          <TextField.Root
            placeholder="v1.2.0 - Add payment integration"
            value={formData.title}
            onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
            required
          />
        </Box>
        
        <Box>
          <Text size="2" weight="medium" mb="1" style={{ display: 'block' }}>
            Description
          </Text>
          <TextArea
            placeholder="Optional description of what this release contains"
            value={formData.description}
            onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
          />
        </Box>
        
        <Flex gap="2" justify="end">
          <Button type="submit" disabled={!formData.service_id || !formData.environment || !formData.title}>
            Create Release
          </Button>
        </Flex>
      </Flex>
    </form>
  )
}

// Release Detail Component
const ReleaseDetail: React.FC<{ release: Release | null }> = ({ release }) => {
  if (!release) return null

  return (
    <Box>
      <Flex direction="column" gap="3">
        <Box>
          <Text weight="medium">Service ID:</Text>
          <Text>{release.service_id}</Text>
        </Box>
        
        <Box>
          <Text weight="medium">Environment:</Text>
          <Text>{release.environment}</Text>
        </Box>
        
        <Box>
          <Text weight="medium">Status:</Text>
          <Badge color={getStatusColor(release.status)} variant="soft">
            {release.status}
          </Badge>
        </Box>
        
        <Box>
          <Text weight="medium">Created By:</Text>
          <Text>{release.created_by}</Text>
        </Box>
        
        <Box>
          <Text weight="medium">Created At:</Text>
          <Text>{new Date(release.created_at).toLocaleString()}</Text>
        </Box>
        
        {release.applied_by && (
          <Box>
            <Text weight="medium">Applied By:</Text>
            <Text>{release.applied_by}</Text>
          </Box>
        )}
        
        {release.applied_at && (
          <Box>
            <Text weight="medium">Applied At:</Text>
            <Text>{new Date(release.applied_at).toLocaleString()}</Text>
          </Box>
        )}
        
        {release.description && (
          <Box>
            <Text weight="medium">Description:</Text>
            <Text>{release.description}</Text>
          </Box>
        )}
        
        <Separator />
        
        <Box>
          <Text weight="medium">Changes:</Text>
          <Text size="2" color="gray">
            {release.changes.length} change(s)
          </Text>
        </Box>
      </Flex>
    </Box>
  )
}

export default ReleasesPage
