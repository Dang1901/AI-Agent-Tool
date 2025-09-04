import { Dialog, Flex, Text, Code, Badge, Separator } from '@radix-ui/themes'
import type { Policy } from '@api/abac'

interface PolicyDetailsDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  policy: Policy | null
}

export default function PolicyDetailsDialog({ open, onOpenChange, policy }: PolicyDetailsDialogProps) {
  if (!policy) return null

  const formatConditions = (conditions: Record<string, any> | undefined) => {
    if (!conditions || Object.keys(conditions).length === 0) {
      return <Text size="2" color="gray">No conditions</Text>
    }

    return (
      <Code variant="soft" size="1" style={{ whiteSpace: 'pre-wrap' }}>
        {JSON.stringify(conditions, null, 2)}
      </Code>
    )
  }

  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Content style={{ maxWidth: 800, maxHeight: '80vh' }}>
        <Dialog.Title>Policy Details</Dialog.Title>
        <Dialog.Description size="2" mb="4">
          View detailed information about the policy
        </Dialog.Description>

        <Flex direction="column" gap="4" style={{ overflow: 'auto' }}>
          {/* Basic Information */}
          <div>
            <Text size="3" weight="bold" mb="2">Basic Information</Text>
            <Flex direction="column" gap="2">
              <Flex justify="between">
                <Text weight="medium">Name:</Text>
                <Text>{policy.name}</Text>
              </Flex>
              <Flex justify="between">
                <Text weight="medium">Type:</Text>
                <Badge color="blue">{policy.policy_type}</Badge>
              </Flex>
              <Flex justify="between">
                <Text weight="medium">Priority:</Text>
                <Badge color="green">{policy.priority}</Badge>
              </Flex>
              <Flex justify="between">
                <Text weight="medium">Effect:</Text>
                <Badge color={policy.effect === 'allow' ? 'green' : 'red'}>
                  {policy.effect.toUpperCase()}
                </Badge>
              </Flex>
              <Flex justify="between">
                <Text weight="medium">Status:</Text>
                <Badge color={policy.is_active ? 'green' : 'red'}>
                  {policy.is_active ? 'Active' : 'Inactive'}
                </Badge>
              </Flex>
              {policy.description && (
                <Flex direction="column" gap="1">
                  <Text weight="medium">Description:</Text>
                  <Text size="2" color="gray">{policy.description}</Text>
                </Flex>
              )}
            </Flex>
          </div>

          <Separator />

          {/* Subject Conditions */}
          <div>
            <Text size="3" weight="bold" mb="2">Subject Conditions</Text>
            <div style={{ maxHeight: 200, overflow: 'auto' }}>
              {formatConditions(policy.subject_conditions)}
            </div>
          </div>

          <Separator />

          {/* Resource Conditions */}
          <div>
            <Text size="3" weight="bold" mb="2">Resource Conditions</Text>
            <div style={{ maxHeight: 200, overflow: 'auto' }}>
              {formatConditions(policy.resource_conditions)}
            </div>
          </div>

          <Separator />

          {/* Action Conditions */}
          <div>
            <Text size="3" weight="bold" mb="2">Action Conditions</Text>
            <div style={{ maxHeight: 200, overflow: 'auto' }}>
              {formatConditions(policy.action_conditions)}
            </div>
          </div>

          <Separator />

          {/* Environment Conditions */}
          <div>
            <Text size="3" weight="bold" mb="2">Environment Conditions</Text>
            <div style={{ maxHeight: 200, overflow: 'auto' }}>
              {formatConditions(policy.environment_conditions)}
            </div>
          </div>

          {/* Obligations */}
          {policy.obligations && Object.keys(policy.obligations).length > 0 && (
            <>
              <Separator />
              <div>
                <Text size="3" weight="bold" mb="2">Obligations</Text>
                <div style={{ maxHeight: 200, overflow: 'auto' }}>
                  <Code variant="soft" size="1" style={{ whiteSpace: 'pre-wrap' }}>
                    {JSON.stringify(policy.obligations, null, 2)}
                  </Code>
                </div>
              </div>
            </>
          )}

          <Separator />

          {/* Timestamps */}
          <div>
            <Text size="3" weight="bold" mb="2">Timestamps</Text>
            <Flex direction="column" gap="2">
              <Flex justify="between">
                <Text weight="medium">Created:</Text>
                <Text size="2" color="gray">
                  {new Date(policy.created_at).toLocaleString()}
                </Text>
              </Flex>
              <Flex justify="between">
                <Text weight="medium">Updated:</Text>
                <Text size="2" color="gray">
                  {new Date(policy.updated_at).toLocaleString()}
                </Text>
              </Flex>
            </Flex>
          </div>
        </Flex>
      </Dialog.Content>
    </Dialog.Root>
  )
}
