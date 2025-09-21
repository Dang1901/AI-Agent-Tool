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
  Switch
} from '@radix-ui/themes'
import { PlusIcon, DownloadIcon, UploadIcon } from '@radix-ui/react-icons'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { envVarApi } from '../../services/api'
import { useToastNotification } from '../../hooks/useToastNotification'
import { DeleteConfirmDialog } from '../../components/ConfirmDialog'

interface EnvVar {
  id: string
  key: string
  value: string
  type: string
  scope: {
    level: string
    ref_id: string
  }
  tags: string[]
  description?: string
  is_secret: boolean
  status: string
  created_by: string
  created_at: string
  updated_by: string
  updated_at: string
}

interface EnvVarsListResponse {
  env_vars: EnvVar[]
  total: number
  page: number
  size: number
}

interface CreateEnvVarData {
  key: string
  value: string
  type: string
  scope_level: string
  scope_ref_id: string
  tags: string[]
  description?: string
  is_secret: boolean
  created_by: string
}

interface UpdateEnvVarData {
  key?: string
  value?: string
  type?: string
  scope_level?: string
  scope_ref_id?: string
  tags?: string[]
  description?: string
  is_secret?: boolean
  updated_by: string
}

const EnvVarsPage: React.FC = () => {
  const [filters, setFilters] = useState({
    scope_level: 'all',
    scope_ref_id: '',
    key_filter: '',
    tag_filter: '',
    type_filter: 'all',
    status_filter: 'all'
  })
  
  const toast = useToastNotification()
  const [page, setPage] = useState(1)
  const [size] = useState(50)
  const [showCreateDialog, setShowCreateDialog] = useState(false)
  const [showRevealDialog, setShowRevealDialog] = useState(false)
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)
  const [selectedEnvVar, setSelectedEnvVar] = useState<EnvVar | null>(null)

  const queryClient = useQueryClient()

  // Fetch environment variables
  const { data: envVarsData, isLoading, error } = useQuery<EnvVarsListResponse>({
    queryKey: ['envvars', filters, page, size],
    queryFn: () => {
      // Convert "all" values to empty strings for API
      const apiFilters = {
        ...filters,
        scope_level: filters.scope_level === 'all' ? '' : filters.scope_level,
        type_filter: filters.type_filter === 'all' ? '' : filters.type_filter,
        status_filter: filters.status_filter === 'all' ? '' : filters.status_filter,
        page,
        size
      }
      return envVarApi.listEnvVars(apiFilters)
    }
  })

  // Create environment variable mutation
  const createMutation = useMutation({
    mutationFn: envVarApi.createEnvVar,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['envvars'] })
      setShowCreateDialog(false)
      toast.showCreateSuccess('Environment Variable')
    },
    onError: (error: any) => {
      toast.showCreateError('Environment Variable', error?.response?.data?.detail || error.message)
    }
  })

  // Update environment variable mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string, data: UpdateEnvVarData }) => envVarApi.updateEnvVar(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['envvars'] })
      toast.showUpdateSuccess('Environment Variable')
    },
    onError: (error: any) => {
      toast.showUpdateError('Environment Variable', error?.response?.data?.detail || error.message)
    }
  })

  // Delete environment variable mutation
  const deleteMutation = useMutation({
    mutationFn: ({ id, deleted_by }: { id: string, deleted_by: string }) => 
      envVarApi.deleteEnvVar(id, deleted_by),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['envvars'] })
      toast.showDeleteSuccess('Environment Variable')
    },
    onError: (error: any) => {
      toast.showDeleteError('Environment Variable', error?.response?.data?.detail || error.message)
    }
  })

  // Reveal secret mutation
  const revealMutation = useMutation({
    mutationFn: ({ id, justification, ttl_seconds, requested_by }: {
      id: string
      justification: string
      ttl_seconds: number
      requested_by: string
    }) => envVarApi.revealSecret(id, justification, ttl_seconds, requested_by),
    onSuccess: (data) => {
      // Show revealed value in a modal with countdown
      console.log('Revealed secret:', data)
      setShowRevealDialog(false)
      toast.showApiSuccess('Secret revealed successfully')
    },
    onError: (error: any) => {
      toast.showApiError('Failed to reveal secret', error?.response?.data?.detail || error.message)
    }
  })

  const handleFilterChange = (key: string, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }))
    setPage(1) // Reset to first page when filtering
  }

  const handleCreateEnvVar = (data: CreateEnvVarData) => {
    createMutation.mutate(data)
  }

  const handleUpdateEnvVar = (id: string, data: UpdateEnvVarData) => {
    updateMutation.mutate({ id, data })
  }

  const handleDeleteEnvVar = (envVar: EnvVar) => {
    setSelectedEnvVar(envVar)
    setShowDeleteDialog(true)
  }

  const confirmDeleteEnvVar = () => {
    if (selectedEnvVar) {
      deleteMutation.mutate({ 
        id: selectedEnvVar.id, 
        deleted_by: 'current_user' 
      })
    }
  }

  const handleRevealSecret = (envVar: EnvVar) => {
    setSelectedEnvVar(envVar)
    setShowRevealDialog(true)
  }

  const handleRevealSubmit = (justification: string, ttl_seconds: number) => {
    if (selectedEnvVar) {
      revealMutation.mutate({
        id: selectedEnvVar.id,
        justification,
        ttl_seconds,
        requested_by: 'current_user'
      })
    }
  }

  if (isLoading) return <div>Loading...</div>
  if (error) return <div>Error: {error.message}</div>

  return (
    <Box p="4">
      <Flex justify="between" align="center" mb="4">
        <Heading size="8">Environment Variables</Heading>
        <Flex gap="2">
          <Button variant="outline" onClick={() => setShowCreateDialog(true)}>
            <PlusIcon />
            Create
          </Button>
          <Button variant="outline">
            <UploadIcon />
            Import
          </Button>
          <Button variant="outline">
            <DownloadIcon />
            Export
          </Button>
        </Flex>
      </Flex>

      {/* Filters */}
      <Card mb="4" style={{ padding: '12px' }}>
        <Flex gap="3" wrap="wrap">
          <Select.Root
            value={filters.scope_level}
            onValueChange={(value) => handleFilterChange('scope_level', value)}
          >
            <Select.Trigger placeholder="Scope Level" />
            <Select.Content>
              <Select.Item value="all">All</Select.Item>
              <Select.Item value="GLOBAL">Global</Select.Item>
              <Select.Item value="PROJECT">Project</Select.Item>
              <Select.Item value="SERVICE">Service</Select.Item>
              <Select.Item value="ENV">Environment</Select.Item>
            </Select.Content>
          </Select.Root>

          <TextField.Root
            placeholder="Scope Ref ID"
            value={filters.scope_ref_id}
            onChange={(e) => handleFilterChange('scope_ref_id', e.target.value)}
          />

          <TextField.Root
            placeholder="Key filter"
            value={filters.key_filter}
            onChange={(e) => handleFilterChange('key_filter', e.target.value)}
          />

          <TextField.Root
            placeholder="Tag filter"
            value={filters.tag_filter}
            onChange={(e) => handleFilterChange('tag_filter', e.target.value)}
          />

          <Select.Root
            value={filters.type_filter}
            onValueChange={(value) => handleFilterChange('type_filter', value)}
          >
            <Select.Trigger placeholder="Type" />
            <Select.Content>
              <Select.Item value="all">All</Select.Item>
              <Select.Item value="STRING">String</Select.Item>
              <Select.Item value="NUMBER">Number</Select.Item>
              <Select.Item value="BOOL">Boolean</Select.Item>
              <Select.Item value="JSON">JSON</Select.Item>
              <Select.Item value="SECRET">Secret</Select.Item>
            </Select.Content>
          </Select.Root>

          <Select.Root
            value={filters.status_filter}
            onValueChange={(value) => handleFilterChange('status_filter', value)}
          >
            <Select.Trigger placeholder="Status" />
            <Select.Content>
              <Select.Item value="all">All</Select.Item>
              <Select.Item value="ACTIVE">Active</Select.Item>
              <Select.Item value="PENDING">Pending</Select.Item>
              <Select.Item value="DEPRECATED">Deprecated</Select.Item>
            </Select.Content>
          </Select.Root>
        </Flex>
      </Card>

      {/* Environment Variables Table */}
      <Card>
        <Table.Root>
          <Table.Header>
            <Table.Row>
              <Table.ColumnHeaderCell>Key</Table.ColumnHeaderCell>
              <Table.ColumnHeaderCell>Value</Table.ColumnHeaderCell>
              <Table.ColumnHeaderCell>Type</Table.ColumnHeaderCell>
              <Table.ColumnHeaderCell>Scope</Table.ColumnHeaderCell>
              <Table.ColumnHeaderCell>Tags</Table.ColumnHeaderCell>
              <Table.ColumnHeaderCell>Status</Table.ColumnHeaderCell>
              <Table.ColumnHeaderCell>Updated By</Table.ColumnHeaderCell>
              <Table.ColumnHeaderCell>Updated At</Table.ColumnHeaderCell>
              <Table.ColumnHeaderCell>Actions</Table.ColumnHeaderCell>
            </Table.Row>
          </Table.Header>
          <Table.Body>
            {envVarsData?.env_vars.map((envVar) => (
              <Table.Row key={envVar.id}>
                <Table.Cell>
                  <Text weight="medium">{envVar.key}</Text>
                </Table.Cell>
                <Table.Cell>
                  <Text>
                    {envVar.is_secret ? '***' : envVar.value}
                  </Text>
                </Table.Cell>
                <Table.Cell>
                  <Badge color={envVar.type === 'SECRET' ? 'red' : 'blue'}>
                    {envVar.type}
                  </Badge>
                </Table.Cell>
                <Table.Cell>
                  <Text size="2">
                    {envVar.scope.level}:{envVar.scope.ref_id}
                  </Text>
                </Table.Cell>
                <Table.Cell>
                  <Flex gap="1" wrap="wrap">
                    {envVar.tags.map((tag) => (
                      <Badge key={tag} variant="soft" size="1">
                        {tag}
                      </Badge>
                    ))}
                  </Flex>
                </Table.Cell>
                <Table.Cell>
                  <Badge 
                    color={envVar.status === 'ACTIVE' ? 'green' : 'orange'}
                    variant="soft"
                  >
                    {envVar.status}
                  </Badge>
                </Table.Cell>
                <Table.Cell>
                  <Text size="2">{envVar.updated_by}</Text>
                </Table.Cell>
                <Table.Cell>
                  <Text size="2">
                    {new Date(envVar.updated_at).toLocaleDateString()}
                  </Text>
                </Table.Cell>
                <Table.Cell>
                  <Flex gap="1">
                    {envVar.is_secret && (
                      <Button
                        size="1"
                        variant="outline"
                        onClick={() => handleRevealSecret(envVar)}
                      >
                        Reveal
                      </Button>
                    )}
                    <Button
                      size="1"
                      variant="outline"
                      onClick={() => handleUpdateEnvVar(envVar.id, { updated_by: 'current_user' })}
                    >
                      Edit
                    </Button>
                    <Button
                      size="1"
                      variant="outline"
                      color="red"
                      onClick={() => handleDeleteEnvVar(envVar)}
                    >
                      Delete
                    </Button>
                  </Flex>
                </Table.Cell>
              </Table.Row>
            ))}
          </Table.Body>
        </Table.Root>
      </Card>

      {/* Pagination */}
      {envVarsData && (
        <Flex justify="between" align="center" mt="4">
          <Text size="2">
            Showing {((page - 1) * size) + 1} to {Math.min(page * size, envVarsData.total)} of {envVarsData.total} results
          </Text>
          <Flex gap="2">
            <Button
              variant="outline"
              disabled={page === 1}
              onClick={() => setPage(page - 1)}
            >
              Previous
            </Button>
            <Button
              variant="outline"
              disabled={page * size >= envVarsData.total}
              onClick={() => setPage(page + 1)}
            >
              Next
            </Button>
          </Flex>
        </Flex>
      )}

      {/* Create Environment Variable Dialog */}
      <Dialog.Root open={showCreateDialog} onOpenChange={setShowCreateDialog}>
        <Dialog.Content>
          <Dialog.Title>Create Environment Variable</Dialog.Title>
          <Dialog.Description>
            Create a new environment variable
          </Dialog.Description>
          
          <Box mt="4">
            <CreateEnvVarForm onSubmit={handleCreateEnvVar} />
          </Box>
        </Dialog.Content>
      </Dialog.Root>

      {/* Reveal Secret Dialog */}
      <Dialog.Root open={showRevealDialog} onOpenChange={setShowRevealDialog}>
        <Dialog.Content>
          <Dialog.Title>Reveal Secret</Dialog.Title>
          <Dialog.Description>
            Reveal the secret value for {selectedEnvVar?.key}
          </Dialog.Description>
          
          <Box mt="4">
            <RevealSecretForm 
              envVar={selectedEnvVar}
              onSubmit={handleRevealSubmit}
            />
          </Box>
        </Dialog.Content>
      </Dialog.Root>

      {/* Delete Confirmation Dialog */}
      <DeleteConfirmDialog
        open={showDeleteDialog}
        onOpenChange={setShowDeleteDialog}
        title="Delete Environment Variable"
        description={`Are you sure you want to delete the environment variable "${selectedEnvVar?.key}"? This action cannot be undone.`}
        onConfirm={confirmDeleteEnvVar}
        loading={deleteMutation.isPending}
      />
    </Box>
  )
}

// Create Environment Variable Form Component
const CreateEnvVarForm: React.FC<{ onSubmit: (data: CreateEnvVarData) => void }> = ({ onSubmit }) => {
  const [formData, setFormData] = useState({
    key: '',
    value: '',
    type: 'STRING',
    scope_level: 'GLOBAL',
    scope_ref_id: '',
    tags: [] as string[],
    description: '',
    is_secret: false,
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
            Key *
          </Text>
          <TextField.Root
            placeholder="DATABASE_URL, API_KEY, etc."
            value={formData.key}
            onChange={(e) => setFormData(prev => ({ ...prev, key: e.target.value }))}
            required
          />
        </Box>
        
        <Box>
          <Text size="2" weight="medium" mb="1" style={{ display: 'block' }}>
            Value *
          </Text>
          <TextArea
            placeholder="Enter the environment variable value"
            value={formData.value}
            onChange={(e) => setFormData(prev => ({ ...prev, value: e.target.value }))}
            required
          />
        </Box>
        
        <Box>
          <Text size="2" weight="medium" mb="1" style={{ display: 'block' }}>
            Type
          </Text>
          <Select.Root
            value={formData.type}
            onValueChange={(value) => setFormData(prev => ({ ...prev, type: value }))}
          >
            <Select.Trigger />
            <Select.Content>
              <Select.Item value="STRING">String - Text value</Select.Item>
              <Select.Item value="NUMBER">Number - Numeric value</Select.Item>
              <Select.Item value="BOOL">Boolean - true/false</Select.Item>
              <Select.Item value="JSON">JSON - Structured data</Select.Item>
              <Select.Item value="SECRET">Secret - Sensitive data</Select.Item>
            </Select.Content>
          </Select.Root>
        </Box>
        
        <Box>
          <Text size="2" weight="medium" mb="1" style={{ display: 'block' }}>
            Scope Level *
          </Text>
          <Select.Root
            value={formData.scope_level}
            onValueChange={(value) => setFormData(prev => ({ ...prev, scope_level: value }))}
          >
            <Select.Trigger />
            <Select.Content>
              <Select.Item value="GLOBAL">Global - Available everywhere</Select.Item>
              <Select.Item value="PROJECT">Project - Specific project</Select.Item>
              <Select.Item value="SERVICE">Service - Specific service</Select.Item>
              <Select.Item value="ENV">Environment - dev/staging/prod</Select.Item>
            </Select.Content>
          </Select.Root>
        </Box>
        
        <Box>
          <Text size="2" weight="medium" mb="1" style={{ display: 'block' }}>
            Scope Reference ID *
          </Text>
          <TextField.Root
            placeholder="project-123, service-name, production, etc."
            value={formData.scope_ref_id}
            onChange={(e) => setFormData(prev => ({ ...prev, scope_ref_id: e.target.value }))}
            required
          />
        </Box>
        
        <Box>
          <Text size="2" weight="medium" mb="1" style={{ display: 'block' }}>
            Tags
          </Text>
          <TextField.Root
            placeholder="database, api, production (comma-separated)"
            value={formData.tags.join(',')}
            onChange={(e) => setFormData(prev => ({ 
              ...prev, 
              tags: e.target.value.split(',').map(t => t.trim()).filter(t => t)
            }))}
          />
        </Box>
        
        <Box>
          <Text size="2" weight="medium" mb="1" style={{ display: 'block' }}>
            Description
          </Text>
          <TextArea
            placeholder="Optional description of this environment variable"
            value={formData.description}
            onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
          />
        </Box>
        
        <Flex align="center" gap="2">
          <Switch
            checked={formData.is_secret}
            onCheckedChange={(checked) => setFormData(prev => ({ ...prev, is_secret: checked }))}
          />
          <Text size="2" weight="medium">Is Secret - Hide value in logs and UI</Text>
        </Flex>
        
        <Flex gap="2" justify="end">
          <Button type="submit" disabled={!formData.key || !formData.value}>
            Create
          </Button>
        </Flex>
      </Flex>
    </form>
  )
}

// Reveal Secret Form Component
const RevealSecretForm: React.FC<{ 
  envVar: EnvVar | null
  onSubmit: (justification: string, ttl_seconds: number) => void 
}> = ({ onSubmit }) => {
  const [justification, setJustification] = useState('')
  const [ttl_seconds, setTtlSeconds] = useState(30)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit(justification, ttl_seconds)
  }

  return (
    <form onSubmit={handleSubmit}>
      <Flex direction="column" gap="3">
        <Box>
          <Text size="2" weight="medium" mb="1" style={{ display: 'block' }}>
            Justification *
          </Text>
          <TextArea
            placeholder="Explain why you need to reveal this secret (e.g., debugging, deployment, etc.)"
            value={justification}
            onChange={(e) => setJustification(e.target.value)}
            required
          />
        </Box>
        
        <Box>
          <Text size="2" weight="medium" mb="1" style={{ display: 'block' }}>
            Time to Live (TTL) in seconds
          </Text>
          <TextField.Root
            type="number"
            placeholder="30"
            value={ttl_seconds}
            onChange={(e) => setTtlSeconds(parseInt(e.target.value) || 30)}
            min="1"
            max="300"
          />
          <Text size="1" color="gray" mt="1" style={{ display: 'block' }}>
            How long the secret will be visible (1-300 seconds)
          </Text>
        </Box>
        
        <Flex gap="2" justify="end">
          <Button type="submit" disabled={!justification}>
            Reveal Secret
          </Button>
        </Flex>
      </Flex>
    </form>
  )
}

export default EnvVarsPage
