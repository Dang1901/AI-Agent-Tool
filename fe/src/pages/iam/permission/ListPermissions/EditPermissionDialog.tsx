import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { Dialog, Button, TextField, TextArea, Flex, Text, Select } from '@radix-ui/themes'
import { useUpdatePermission } from '@applications/queries/rbac'
import type { Permission } from '@api/rbac'

interface EditPermissionDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  permission: Permission | null
}

interface FormData {
  name: string
  display_name: string
  description?: string
  resource: string
  action: string
  is_active: boolean
}

const resourceOptions = [
  { value: 'user', label: 'User' },
  { value: 'role', label: 'Role' },
  { value: 'permission', label: 'Permission' },
  { value: 'policy', label: 'Policy' },
  { value: 'resource', label: 'Resource' },
  { value: 'attribute', label: 'Attribute' },
]

const actionOptions = [
  { value: 'create', label: 'Create' },
  { value: 'read', label: 'Read' },
  { value: 'update', label: 'Update' },
  { value: 'delete', label: 'Delete' },
  { value: 'list', label: 'List' },
  { value: 'assign', label: 'Assign' },
  { value: 'revoke', label: 'Revoke' },
]

export default function EditPermissionDialog({ open, onOpenChange, permission }: EditPermissionDialogProps) {
  const updatePermissionMutation = useUpdatePermission()

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    watch,
  } = useForm<FormData>({
    defaultValues: {
      name: '',
      display_name: '',
      description: '',
      resource: 'user',
      action: 'read',
      is_active: true,
    },
  })

  useEffect(() => {
    if (permission) {
      reset({
        name: permission.name,
        display_name: permission.display_name,
        description: permission.description || '',
        resource: permission.resource,
        action: permission.action,
        is_active: permission.is_active,
      })
    }
  }, [permission, reset])

  const onSubmit = async (data: FormData) => {
    if (!permission) return

    try {
      await updatePermissionMutation.mutateAsync({ id: permission.id, data })
      onOpenChange(false)
    } catch (error) {
      console.error('Failed to update permission:', error)
    }
  }

  const handleOpenChange = (open: boolean) => {
    if (!open) {
      reset()
    }
    onOpenChange(open)
  }

  if (!permission) return null

  return (
    <Dialog.Root open={open} onOpenChange={handleOpenChange}>
      <Dialog.Content style={{ maxWidth: 500 }}>
        <Dialog.Title>Edit Permission</Dialog.Title>
        <Dialog.Description size="2" mb="4">
          Update permission information and settings
        </Dialog.Description>

        <form onSubmit={handleSubmit(onSubmit)}>
          <Flex direction="column" gap="4">
            <div>
              <Text as="label" size="2" weight="medium">
                Permission Name *
              </Text>
              <TextField.Root
                placeholder="e.g., user.read, role.create"
                {...register('name', { required: 'Permission name is required' })}
              />
              {errors.name && (
                <Text size="1" color="red">
                  {errors.name.message}
                </Text>
              )}
            </div>

            <div>
              <Text as="label" size="2" weight="medium">
                Display Name *
              </Text>
              <TextField.Root
                placeholder="e.g., Read Users, Create Roles"
                {...register('display_name', { required: 'Display name is required' })}
              />
              {errors.display_name && (
                <Text size="1" color="red">
                  {errors.display_name.message}
                </Text>
              )}
            </div>

            <div>
              <Text as="label" size="2" weight="medium">
                Description
              </Text>
              <TextArea
                placeholder="Describe what this permission allows"
                {...register('description')}
              />
            </div>

            <Flex gap="3">
              <div style={{ flex: 1 }}>
                <Text as="label" size="2" weight="medium">
                  Resource *
                </Text>
                <Select.Root
                  value={watch('resource')}
                  onValueChange={(value) => register('resource').onChange({ target: { value } })}
                >
                  <Select.Trigger />
                  <Select.Content>
                    {resourceOptions.map((option) => (
                      <Select.Item key={option.value} value={option.value}>
                        {option.label}
                      </Select.Item>
                    ))}
                  </Select.Content>
                </Select.Root>
              </div>

              <div style={{ flex: 1 }}>
                <Text as="label" size="2" weight="medium">
                  Action *
                </Text>
                <Select.Root
                  value={watch('action')}
                  onValueChange={(value) => register('action').onChange({ target: { value } })}
                >
                  <Select.Trigger />
                  <Select.Content>
                    {actionOptions.map((option) => (
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

            <Flex gap="3" justify="end" mt="4">
              <Dialog.Close>
                <Button variant="soft" color="gray">
                  Cancel
                </Button>
              </Dialog.Close>
              <Button
                type="submit"
                disabled={updatePermissionMutation.isPending}
              >
                {updatePermissionMutation.isPending ? 'Updating...' : 'Update Permission'}
              </Button>
            </Flex>
          </Flex>
        </form>
      </Dialog.Content>
    </Dialog.Root>
  )
}