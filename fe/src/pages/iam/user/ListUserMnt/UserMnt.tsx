import { DataTable, type DataTableColumn } from '@components/DataTable'
import { useMemo, useState } from 'react'
import HeaderInformation from '@components/HeaderInformation'
import { Button, Flex, Text } from '@radix-ui/themes'
import { PlusIcon } from '@radix-ui/react-icons'

type UserRow = {
  id: number
  name: string
  email: string
  role: string
}

export default function UserMnt() {
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)

  // demo data
  const allRows: UserRow[] = useMemo(
    () =>
      Array.from({ length: 87 }).map((_, i) => ({
        id: i + 1,
        name: `User ${i + 1}`,
        email: `user${i + 1}@example.com`,
        role: i % 3 === 0 ? 'Admin' : i % 3 === 1 ? 'Editor' : 'Viewer',
      })),
    []
  )

  const start = (page - 1) * pageSize
  const data = allRows.slice(start, start + pageSize)
  const total = allRows.length

  const columns: Array<DataTableColumn<UserRow>> = [
    { key: 'id', header: 'ID', width: 80 },
    {
      key: 'name',
      header: 'Name',
      render: (row) => <a href={`/iam/users/${row.id}?tab=profile`}>{row.name}</a>,
    },
    { key: 'email', header: 'Email' },
    { key: 'role', header: 'Role' },
  ]

  return (
    <Flex direction="column" gap="4">
      <HeaderInformation
        breadcrumb={<Text as="span">Users</Text>}
        title="User Management"
        description="Manage user accounts, roles and access."
        action={<Button><PlusIcon /> Create user</Button>}
      />

      <DataTable
        data={data}
        columns={columns}
        page={page}
        pageSize={pageSize}
        total={total}
        onPageChange={setPage}
        onPageSizeChange={(size: number) => {
          setPageSize(size)
          setPage(1)
        }}
      />
    </Flex>
  )
}