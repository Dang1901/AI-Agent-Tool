import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { Dialog, Button, TextField, TextArea, Flex, Text } from '@radix-ui/themes'
import { useUpdateRole } from '@applications/queries/rbac'
import type { Role } from '@api/rbac'

interface EditRoleDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  role: Role | null
}

interface FormData {
  name: string
  display_name: string
  description?: string
  is_active: boolean
}

export default function EditRoleDialog({ open, onOpenChange, role }: EditRoleDialogProps) {
  const updateRoleMutation = useUpdateRole()

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
      is_active: true,
    },
  })

  const isActive = watch('is_active')

  useEffect(() => {
    if (role) {
      reset({
        name: role.name,
        display_name: role.display_name,
        description: role.description || '',
        is_active: role.is_active,
      })
    }
  }, [role, reset])

  const onSubmit = async (data: FormData) => {
    if (!role) return

    try {
      await updateRoleMutation.mutateAsync({ id: role.id, data })
      onOpenChange(false)
    } catch (error) {
      console.error('Failed to update role:', error)
    }
  }

  const handleOpenChange = (open: boolean) => {
    if (!open) {
      reset()
    }
    onOpenChange(open)
  }

  if (!role) return null

  return (
    <Dialog.Root open={open} onOpenChange={handleOpenChange}>
      <Dialog.Content style={{ maxWidth: 500 }}>
        <Dialog.Title>Edit Role</Dialog.Title>
        <Dialog.Description size="2" mb="4">
          Update role information and settings
        </Dialog.Description>

        <form onSubmit={handleSubmit(onSubmit)}>
          <Flex direction="column" gap="4">
            <div>
              <Text as="label" size="2" weight="medium">
                Role Name *
              </Text>
              <TextField.Root
                placeholder="e.g., admin, manager, user"
                {...register('name', { required: 'Role name is required' })}
                disabled={role.is_system}
              />
              {errors.name && (
                <Text size="1" color="red">
                  {errors.name.message}
                </Text>
              )}
              {role.is_system && (
                <Text size="1" color="gray">
                  System roles cannot be renamed
                </Text>
              )}
            </div>

            <div>
              <Text as="label" size="2" weight="medium">
                Display Name *
              </Text>
              <TextField.Root
                placeholder="e.g., Administrator, Manager, User"
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
                placeholder="Describe the role's purpose and responsibilities"
                {...register('description')}
              />
            </div>

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
                disabled={updateRoleMutation.isPending}
              >
                {updateRoleMutation.isPending ? 'Updating...' : 'Update Role'}
              </Button>
            </Flex>
          </Flex>
        </form>
      </Dialog.Content>
    </Dialog.Root>
  )
}
