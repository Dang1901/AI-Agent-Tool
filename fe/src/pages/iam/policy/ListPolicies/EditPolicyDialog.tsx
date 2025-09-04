import { useForm } from 'react-hook-form'
import { Dialog, Button, TextField, TextArea, Flex, Text, Select } from '@radix-ui/themes'
import { useUpdatePolicy } from '@applications/queries/abac'
import { useState, useEffect } from 'react'
import type { Policy } from '@api/abac'

interface EditPolicyDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  policy: Policy | null
}

interface FormData {
  name: string
  description?: string
  policy_type: string
  priority: number
  is_active: boolean
  subject_conditions?: string
  resource_conditions?: string
  action_conditions?: string
  environment_conditions?: string
  effect: string
  obligations?: string
}

const policyTypeOptions = [
  { value: 'allow', label: 'Allow' },
  { value: 'deny', label: 'Deny' },
  { value: 'conditional', label: 'Conditional' },
]

const effectOptions = [
  { value: 'allow', label: 'Allow' },
  { value: 'deny', label: 'Deny' },
]

export default function EditPolicyDialog({ open, onOpenChange, policy }: EditPolicyDialogProps) {
  const updatePolicyMutation = useUpdatePolicy()
  const [jsonErrors, setJsonErrors] = useState<Record<string, string>>({})

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    watch,
  } = useForm<FormData>({
    defaultValues: {
      name: '',
      description: '',
      policy_type: 'conditional',
      priority: 100,
      is_active: true,
      subject_conditions: '',
      resource_conditions: '',
      action_conditions: '',
      environment_conditions: '',
      effect: 'allow',
      obligations: '',
    },
  })

  // Reset form when policy changes
  useEffect(() => {
    if (policy) {
      reset({
        name: policy.name,
        description: policy.description || '',
        policy_type: policy.policy_type,
        priority: policy.priority,
        is_active: policy.is_active,
        subject_conditions: policy.subject_conditions ? JSON.stringify(policy.subject_conditions, null, 2) : '',
        resource_conditions: policy.resource_conditions ? JSON.stringify(policy.resource_conditions, null, 2) : '',
        action_conditions: policy.action_conditions ? JSON.stringify(policy.action_conditions, null, 2) : '',
        environment_conditions: policy.environment_conditions ? JSON.stringify(policy.environment_conditions, null, 2) : '',
        effect: policy.effect,
        obligations: policy.obligations ? JSON.stringify(policy.obligations, null, 2) : '',
      })
    }
  }, [policy, reset])

  const validateJson = (jsonString: string, fieldName: string): boolean => {
    if (!jsonString.trim()) return true
    
    try {
      JSON.parse(jsonString)
      setJsonErrors(prev => ({ ...prev, [fieldName]: '' }))
      return true
    } catch (error) {
      setJsonErrors(prev => ({ 
        ...prev, 
        [fieldName]: `Invalid JSON: ${error instanceof Error ? error.message : 'Unknown error'}` 
      }))
      return false
    }
  }

  const onSubmit = async (data: FormData) => {
    if (!policy) return

    // Validate JSON fields
    const jsonFields = ['subject_conditions', 'resource_conditions', 'action_conditions', 'environment_conditions', 'obligations']
    let hasErrors = false

    for (const field of jsonFields) {
      const value = data[field as keyof FormData] as string
      if (!validateJson(value, field)) {
        hasErrors = true
      }
    }

    if (hasErrors) return

    // Parse JSON fields
    const policyData = {
      ...data,
      subject_conditions: data.subject_conditions ? JSON.parse(data.subject_conditions) : undefined,
      resource_conditions: data.resource_conditions ? JSON.parse(data.resource_conditions) : undefined,
      action_conditions: data.action_conditions ? JSON.parse(data.action_conditions) : undefined,
      environment_conditions: data.environment_conditions ? JSON.parse(data.environment_conditions) : undefined,
      obligations: data.obligations ? JSON.parse(data.obligations) : undefined,
    }

    try {
      await updatePolicyMutation.mutateAsync({ id: policy.id, data: policyData })
      onOpenChange(false)
    } catch (error) {
      console.error('Failed to update policy:', error)
    }
  }

  const handleOpenChange = (open: boolean) => {
    if (!open) {
      setJsonErrors({})
    }
    onOpenChange(open)
  }

  if (!policy) return null

  return (
    <Dialog.Root open={open} onOpenChange={handleOpenChange}>
      <Dialog.Content style={{ maxWidth: 800, maxHeight: '90vh' }}>
        <Dialog.Title>Edit Policy</Dialog.Title>
        <Dialog.Description size="2" mb="4">
          Update the ABAC policy settings
        </Dialog.Description>

        <form onSubmit={handleSubmit(onSubmit)}>
          <Flex direction="column" gap="4" style={{ overflow: 'auto', maxHeight: '70vh' }}>
            {/* Basic Information */}
            <div>
              <Text size="3" weight="bold" mb="2">Basic Information</Text>
              <Flex direction="column" gap="3">
                <div>
                  <Text as="label" size="2" weight="medium">
                    Policy Name *
                  </Text>
                  <TextField.Root
                    placeholder="e.g., Department Access Policy"
                    {...register('name', { required: 'Policy name is required' })}
                  />
                  {errors.name && (
                    <Text size="1" color="red">
                      {errors.name.message}
                    </Text>
                  )}
                </div>

                <div>
                  <Text as="label" size="2" weight="medium">
                    Description
                  </Text>
                  <TextArea
                    placeholder="Describe the policy's purpose"
                    {...register('description')}
                  />
                </div>

                <Flex gap="3">
                  <div style={{ flex: 1 }}>
                    <Text as="label" size="2" weight="medium">
                      Policy Type *
                    </Text>
                    <Select.Root
                      value={watch('policy_type')}
                      onValueChange={(value) => register('policy_type').onChange({ target: { value } })}
                    >
                      <Select.Trigger />
                      <Select.Content>
                        {policyTypeOptions.map((option) => (
                          <Select.Item key={option.value} value={option.value}>
                            {option.label}
                          </Select.Item>
                        ))}
                      </Select.Content>
                    </Select.Root>
                  </div>

                  <div style={{ flex: 1 }}>
                    <Text as="label" size="2" weight="medium">
                      Priority *
                    </Text>
                    <TextField.Root
                      type="number"
                      placeholder="100"
                      {...register('priority', { 
                        required: 'Priority is required',
                        valueAsNumber: true,
                        min: { value: 1, message: 'Priority must be at least 1' }
                      })}
                    />
                    {errors.priority && (
                      <Text size="1" color="red">
                        {errors.priority.message}
                      </Text>
                    )}
                  </div>

                  <div style={{ flex: 1 }}>
                    <Text as="label" size="2" weight="medium">
                      Effect *
                    </Text>
                    <Select.Root
                      value={watch('effect')}
                      onValueChange={(value) => register('effect').onChange({ target: { value } })}
                    >
                      <Select.Trigger />
                      <Select.Content>
                        {effectOptions.map((option) => (
                          <Select.Item key={option.value} value={option.value}>
                            {option.label}
                          </Select.Item>
                        ))}
                      </Select.Content>
                    </Select.Root>
                  </div>
                </Flex>

                <div>
                  <Flex align="center" gap="2">
                    <input
                      type="checkbox"
                      id="is_active"
                      {...register('is_active')}
                    />
                    <Text as="label" htmlFor="is_active" size="2">
                      Active
                    </Text>
                  </Flex>
                </div>
              </Flex>
            </div>

            {/* Conditions */}
            <div>
              <Text size="3" weight="bold" mb="2">Conditions (JSON Format)</Text>
              <Flex direction="column" gap="3">
                <div>
                  <Text as="label" size="2" weight="medium">
                    Subject Conditions
                  </Text>
                  <TextArea
                    placeholder='{"user.department": "IT", "user.clearance_level": {"operator": "gte", "value": "internal"}}'
                    {...register('subject_conditions')}
                    style={{ fontFamily: 'monospace', minHeight: 100 }}
                  />
                  {jsonErrors.subject_conditions && (
                    <Text size="1" color="red">
                      {jsonErrors.subject_conditions}
                    </Text>
                  )}
                </div>

                <div>
                  <Text as="label" size="2" weight="medium">
                    Resource Conditions
                  </Text>
                  <TextArea
                    placeholder='{"resource.sensitivity": {"operator": "in", "value": ["confidential", "secret"]}}'
                    {...register('resource_conditions')}
                    style={{ fontFamily: 'monospace', minHeight: 100 }}
                  />
                  {jsonErrors.resource_conditions && (
                    <Text size="1" color="red">
                      {jsonErrors.resource_conditions}
                    </Text>
                  )}
                </div>

                <div>
                  <Text as="label" size="2" weight="medium">
                    Action Conditions
                  </Text>
                  <TextArea
                    placeholder='{"action": {"operator": "in", "value": ["read", "write"]}}'
                    {...register('action_conditions')}
                    style={{ fontFamily: 'monospace', minHeight: 100 }}
                  />
                  {jsonErrors.action_conditions && (
                    <Text size="1" color="red">
                      {jsonErrors.action_conditions}
                    </Text>
                  )}
                </div>

                <div>
                  <Text as="label" size="2" weight="medium">
                    Environment Conditions
                  </Text>
                  <TextArea
                    placeholder='{"env.time": {"operator": "regex", "value": "^(0[8-9]|1[0-7]):\\d{2}$"}}'
                    {...register('environment_conditions')}
                    style={{ fontFamily: 'monospace', minHeight: 100 }}
                  />
                  {jsonErrors.environment_conditions && (
                    <Text size="1" color="red">
                      {jsonErrors.environment_conditions}
                    </Text>
                  )}
                </div>

                <div>
                  <Text as="label" size="2" weight="medium">
                    Obligations
                  </Text>
                  <TextArea
                    placeholder='{"log": true, "notify": ["admin@company.com"]}'
                    {...register('obligations')}
                    style={{ fontFamily: 'monospace', minHeight: 100 }}
                  />
                  {jsonErrors.obligations && (
                    <Text size="1" color="red">
                      {jsonErrors.obligations}
                    </Text>
                  )}
                </div>
              </Flex>
            </div>

            <Flex gap="3" justify="end" mt="4">
              <Dialog.Close>
                <Button variant="soft" color="gray">
                  Cancel
                </Button>
              </Dialog.Close>
              <Button
                type="submit"
                disabled={updatePolicyMutation.isPending}
              >
                {updatePolicyMutation.isPending ? 'Updating...' : 'Update Policy'}
              </Button>
            </Flex>
          </Flex>
        </form>
      </Dialog.Content>
    </Dialog.Root>
  )
}
