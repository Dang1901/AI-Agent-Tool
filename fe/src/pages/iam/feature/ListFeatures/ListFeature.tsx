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

export default function ListFeatures() {
    const [page, setPage] = useState(1)
    const [pageSize, setPageSize] = useState(10)


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
                breadcrumb={<Text as="span">Features</Text>}                       
                title="Feature Management"
                description="Manage system features for access control and permissions."
                action={<Button><PlusIcon /> Create feature</Button>}
            />


            <DataTable
                data={[]}
                columns={columns}
                page={page}
                pageSize={pageSize}
                total={0}
                onPageChange={setPage}
                onPageSizeChange={(size: number) => {
                    setPageSize(size)
                    setPage(1)
                }}
            />
        </Flex>
    )
}