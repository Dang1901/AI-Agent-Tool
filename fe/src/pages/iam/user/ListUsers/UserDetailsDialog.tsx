import { Dialog, Button, Flex, Text, Badge, Separator } from '@radix-ui/themes'
import type { User } from '@api/user'

interface UserDetailsDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  user: User | null
}

export default function UserDetailsDialog({ open, onOpenChange, user }: UserDetailsDialogProps) {
  if (!user) return null

  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Content style={{ maxWidth: 600 }}>
        <Dialog.Title>User Details</Dialog.Title>
        <Dialog.Description size="2" mb="4">
          View detailed information about this user
        </Dialog.Description>

        <Flex direction="column" gap="4">
          {/* Basic Info */}
          <div>
            <Text size="3" weight="bold" mb="2">Basic Information</Text>
            <Flex direction="column" gap="2">
              <Flex justify="between">
                <Text size="2" weight="medium">Name:</Text>
                <Text size="2">{user.name || 'N/A'}</Text>
              </Flex>
              <Flex justify="between">
                <Text size="2" weight="medium">Email:</Text>
                <Text size="2">{user.email}</Text>
              </Flex>
              <Flex justify="between">
                <Text size="2" weight="medium">Phone:</Text>
                <Text size="2">{user.phone_number || 'N/A'}</Text>
              </Flex>
              <Flex justify="between">
                <Text size="2" weight="medium">Gender:</Text>
                <Text size="2">{user.gender || 'N/A'}</Text>
              </Flex>
              <Flex justify="between">
                <Text size="2" weight="medium">Date of Birth:</Text>
                <Text size="2">{user.dob || 'N/A'}</Text>
              </Flex>
            </Flex>
          </div>

          <Separator />

          {/* Work Info */}
          <div>
            <Text size="3" weight="bold" mb="2">Work Information</Text>
            <Flex direction="column" gap="2">
              <Flex justify="between">
                <Text size="2" weight="medium">Department:</Text>
                <Text size="2">{user.department || 'N/A'}</Text>
              </Flex>
              <Flex justify="between">
                <Text size="2" weight="medium">Position:</Text>
                <Text size="2">{user.position || 'N/A'}</Text>
              </Flex>
              <Flex justify="between">
                <Text size="2" weight="medium">Location:</Text>
                <Text size="2">{user.location || 'N/A'}</Text>
              </Flex>
              <Flex justify="between">
                <Text size="2" weight="medium">Clearance Level:</Text>
                <Badge color="blue" variant="soft">
                  {user.clearance_level || 'N/A'}
                </Badge>
              </Flex>
            </Flex>
          </div>

          <Separator />

          {/* Status Info */}
          <div>
            <Text size="3" weight="bold" mb="2">Status Information</Text>
            <Flex direction="column" gap="2">
              <Flex justify="between">
                <Text size="2" weight="medium">Account Status:</Text>
                <Badge color={user.is_active ? 'green' : 'red'}>
                  {user.is_active ? 'Active' : 'Inactive'}
                </Badge>
              </Flex>
              <Flex justify="between">
                <Text size="2" weight="medium">Verification Status:</Text>
                <Badge color={user.is_verified ? 'green' : 'orange'}>
                  {user.is_verified ? 'Verified' : 'Pending'}
                </Badge>
              </Flex>
              <Flex justify="between">
                <Text size="2" weight="medium">Last Login:</Text>
                <Text size="2">{new Date(user.updated_at).toLocaleString()}</Text>
              </Flex>
              <Flex justify="between">
                <Text size="2" weight="medium">Account Created:</Text>
                <Text size="2">{new Date(user.created_at).toLocaleString()}</Text>
              </Flex>
            </Flex>
          </div>

          <Separator />

          {/* Actions */}
          <Flex gap="3" justify="end" mt="4">
            <Dialog.Close>
              <Button variant="soft" color="gray">
                Close
              </Button>
            </Dialog.Close>
          </Flex>
        </Flex>
      </Dialog.Content>
    </Dialog.Root>
  )
}
