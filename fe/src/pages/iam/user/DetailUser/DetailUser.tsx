import { useParams, useSearchParams } from 'react-router-dom'
import HeaderInformation from '@components/HeaderInformation'
import { Button, Flex } from '@radix-ui/themes'
import { Pencil2Icon } from '@radix-ui/react-icons'
import UserProfile from './src/PermissionUser/ListPermissionUser/UserProfile'
import UserRoles from './src/UserRoles'
import UserActivity from './src/UserActivity'
import { useState } from 'react'

export default function UserDetail() {
  const { id } = useParams<{ id: string }>()
  const userName = `User ${id}`
  const [searchParams, setSearchParams] = useSearchParams()
  const [isEditOpen, setEditOpen] = useState(false);
  const current = searchParams.get('tab') || 'profile'
  const tabValues = [
    { key: 'profile', label: 'Profile' },
    { key: 'roles', label: 'Roles' },
    { key: 'activity', label: 'Activity' }
  ]

  return (
    <Flex direction="column" gap="4">
      <HeaderInformation
        breadcrumbs={[{ label: 'Users', to: '/iam/users' }, { label: userName }]}
        title={userName}
        description={`User ID: ${id}`}
        action={<Button onClick={() => setEditOpen(true)}>
          <Pencil2Icon /> Edit
        </Button>}
        tabs={tabValues}
        activeTabKey={current}
        onTabChange={(k) => setSearchParams({ tab: k })}
      />

      {current === 'roles' ? <UserRoles /> : current === 'activity' ? <UserActivity /> : <UserProfile />}
    </Flex>
  )
}


