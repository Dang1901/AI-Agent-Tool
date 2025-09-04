import { useForm } from 'react-hook-form'
import { Dialog, Button, TextField, TextArea, Flex, Text } from '@radix-ui/themes'
import { useCreateRole } from '@applications/queries/rbac'

interface CreateRoleDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

interface FormData {
  name: string
  display_name: string
  description?: string
}

export default function CreateRoleDialog({ open, onOpenChange }: CreateRoleDialogProps) {
  const createRoleMutation = useCreateRole()

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<FormData>({
    defaultValues: {
      name: '',
      display_name: '',
      description: '',
    },
  })

  const onSubmit = async (data: FormData) => {
    try {
      await createRoleMutation.mutateAsync(data)
      reset()
      onOpenChange(false)
    } catch (error) {
      console.error('Failed to create role:', error)
    }
  }

  const handleOpenChange = (open: boolean) => {
    if (!open) {
      reset()
    }
    onOpenChange(open)
  }

  return (
    <Dialog.Root open={open} onOpenChange={handleOpenChange}>
      <Dialog.Content style={{ maxWidth: 500 }}>
        <Dialog.Title>Create New Role</Dialog.Title>
        <Dialog.Description size="2" mb="4">
          Create a new role with specific permissions
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

            <Flex gap="3" justify="end" mt="4">
              <Dialog.Close>
                <Button variant="soft" color="gray">
                  Cancel
                </Button>
              </Dialog.Close>
              <Button
                type="submit"
                disabled={createRoleMutation.isPending}
              >
                {createRoleMutation.isPending ? 'Creating...' : 'Create Role'}
              </Button>
            </Flex>
          </Flex>
        </form>
      </Dialog.Content>
    </Dialog.Root>
  )
}
