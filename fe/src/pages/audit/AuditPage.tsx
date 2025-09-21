import React, { useState } from 'react'
import { 
  Box, 
  Card, 
  Flex, 
  Heading, 
  Text, 
  TextField, 
  Select, 
  Badge,
  Table
} from '@radix-ui/themes'
import { useQuery } from '@tanstack/react-query'
import { auditApi } from '../../services/api'

interface AuditEvent {
  id: string
  actor: string
  action: string
  target_type: string
  target_id: string
  before_json?: Record<string, unknown>
  after_json?: Record<string, unknown>
  reason?: string
  timestamp: string
  action_description: string
  change_summary: string
  is_sensitive: boolean
}

interface AuditEventsResponse {
  events: AuditEvent[]
  total: number
  page: number
  size: number
}

const AuditPage: React.FC = () => {
  const [filters, setFilters] = useState({
    actor: '',
    action: 'all',
    target_type: 'all',
    target_id: ''
  })
  const [page, setPage] = useState(1)
  const [size] = useState(50)

  // Fetch audit events
  const { data: auditData, isLoading, error } = useQuery<AuditEventsResponse>({
    queryKey: ['audit', filters, page, size],
    queryFn: () => {
      // Convert "all" values to empty strings for API
      const apiFilters = {
        ...filters,
        action: filters.action === 'all' ? '' : filters.action,
        target_type: filters.target_type === 'all' ? '' : filters.target_type,
        page,
        size
      }
      return auditApi.getAuditEvents(apiFilters)
    }
  })

  const auditEvents = auditData?.events || []

  const handleFilterChange = (key: string, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }))
    setPage(1)
  }

  if (isLoading) return <div>Loading...</div>
  if (error) return <div>Error: {error.message}</div>

  return (
    <Box p="4">
      <Flex justify="between" align="center" mb="4">
        <Heading size="8">Audit Log</Heading>
        <Text size="2" color="gray">
          Track all changes and activities
        </Text>
      </Flex>

      {/* Filters */}
      <Card mb="4" style={{ padding: '12px' }}>
        <Flex gap="3" wrap="wrap">
          <TextField.Root
            placeholder="Actor"
            value={filters.actor}
            onChange={(e) => handleFilterChange('actor', e.target.value)}
          />

          <Select.Root
            value={filters.action}
            onValueChange={(value) => handleFilterChange('action', value)}
          >
            <Select.Trigger placeholder="Action" />
            <Select.Content>
              <Select.Item value="all">All</Select.Item>
              <Select.Item value="CREATE">Create</Select.Item>
              <Select.Item value="UPDATE">Update</Select.Item>
              <Select.Item value="DELETE">Delete</Select.Item>
              <Select.Item value="REVEAL">Reveal</Select.Item>
              <Select.Item value="APPROVE">Approve</Select.Item>
              <Select.Item value="REJECT">Reject</Select.Item>
              <Select.Item value="APPLY">Apply</Select.Item>
              <Select.Item value="ROLLBACK">Rollback</Select.Item>
              <Select.Item value="EXPORT">Export</Select.Item>
              <Select.Item value="IMPORT">Import</Select.Item>
            </Select.Content>
          </Select.Root>

          <Select.Root
            value={filters.target_type}
            onValueChange={(value) => handleFilterChange('target_type', value)}
          >
            <Select.Trigger placeholder="Target Type" />
            <Select.Content>
              <Select.Item value="all">All</Select.Item>
              <Select.Item value="ENV_VAR">Environment Variable</Select.Item>
              <Select.Item value="RELEASE">Release</Select.Item>
              <Select.Item value="APPROVAL">Approval</Select.Item>
              <Select.Item value="POLICY">Policy</Select.Item>
            </Select.Content>
          </Select.Root>

          <TextField.Root
            placeholder="Target ID"
            value={filters.target_id}
            onChange={(e) => handleFilterChange('target_id', e.target.value)}
          />
        </Flex>
      </Card>

      {/* Audit Events Table */}
      <Card>
        <Table.Root>
          <Table.Header>
            <Table.Row>
              <Table.ColumnHeaderCell>Timestamp</Table.ColumnHeaderCell>
              <Table.ColumnHeaderCell>Actor</Table.ColumnHeaderCell>
              <Table.ColumnHeaderCell>Action</Table.ColumnHeaderCell>
              <Table.ColumnHeaderCell>Target</Table.ColumnHeaderCell>
              <Table.ColumnHeaderCell>Description</Table.ColumnHeaderCell>
              <Table.ColumnHeaderCell>Changes</Table.ColumnHeaderCell>
            </Table.Row>
          </Table.Header>
          <Table.Body>
            {auditEvents?.map((event) => (
              <Table.Row key={event.id}>
                <Table.Cell>
                  <Text size="2">
                    {new Date(event.timestamp).toLocaleString()}
                  </Text>
                </Table.Cell>
                <Table.Cell>
                  <Text weight="medium">{event.actor}</Text>
                </Table.Cell>
                <Table.Cell>
                  <Badge 
                    color={getActionColor(event.action)}
                    variant="soft"
                  >
                    {event.action}
                  </Badge>
                </Table.Cell>
                <Table.Cell>
                  <Text size="2">
                    {event.target_type}: {event.target_id}
                  </Text>
                </Table.Cell>
                <Table.Cell>
                  <Text size="2">{event.action_description}</Text>
                  {event.reason && (
                    <Text size="1" color="gray" style={{ display: 'block' }}>
                      Reason: {event.reason}
                    </Text>
                  )}
                </Table.Cell>
                <Table.Cell>
                  <Text size="2">{event.change_summary}</Text>
                  {event.is_sensitive && (
                    <Badge color="red" variant="soft" size="1">
                      Sensitive
                    </Badge>
                  )}
                </Table.Cell>
              </Table.Row>
            ))}
          </Table.Body>
        </Table.Root>
      </Card>

      {/* Recent Events */}
      <Card mt="4">
        <Box style={{ padding: '12px' }}>
          <Heading size="4" mb="3">Recent Events</Heading>
          <Flex direction="column" gap="2">
            {auditEvents?.slice(0, 10).map((event) => (
              <Box key={event.id} style={{ padding: '8px', border: '1px solid var(--gray-6)', borderRadius: '6px' }}>
                <Flex justify="between" align="center" mb="1">
                  <Text weight="medium">{event.actor}</Text>
                  <Text size="2" color="gray">
                    {new Date(event.timestamp).toLocaleString()}
                  </Text>
                </Flex>
                <Text size="2" mb="1">{event.action_description}</Text>
                <Text size="1" color="gray">{event.change_summary}</Text>
                {event.is_sensitive && (
                  <Badge color="red" variant="soft" size="1" style={{ marginTop: '4px' }}>
                    Sensitive Action
                  </Badge>
                )}
              </Box>
            ))}
          </Flex>
        </Box>
      </Card>
    </Box>
  )
}

// Helper function to get action color
const getActionColor = (action: string) => {
  switch (action) {
    case 'CREATE': return 'green'
    case 'UPDATE': return 'blue'
    case 'DELETE': return 'red'
    case 'REVEAL': return 'orange'
    case 'APPROVE': return 'green'
    case 'REJECT': return 'red'
    case 'APPLY': return 'blue'
    case 'ROLLBACK': return 'orange'
    case 'EXPORT': return 'purple'
    case 'IMPORT': return 'purple'
    default: return 'gray'
  }
}

export default AuditPage
