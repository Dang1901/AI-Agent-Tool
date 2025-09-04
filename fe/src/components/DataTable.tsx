import { Card, Flex, ScrollArea, Table, Text } from '@radix-ui/themes'
import { ChevronLeftIcon, ChevronRightIcon } from '@radix-ui/react-icons'

export type DataTableColumn<T = Record<string, unknown>> = {
  key: keyof T | string
  header: string
  width?: number | string
  render?: (row: T) => React.ReactNode
}

type DataTableProps<T = Record<string, unknown>> = {
  data: T[]
  columns: Array<DataTableColumn<T>>
  page: number
  pageSize: number
  total: number
  loading?: boolean
  onPageChange?: (page: number) => void
  onPageSizeChange?: (pageSize: number) => void
}

export function DataTable<T = Record<string, unknown>>({
  data,
  columns,
  page,
  pageSize,
  total,
  loading,
  onPageChange,
  onPageSizeChange,
}: DataTableProps<T>) {
  const totalPages = Math.max(1, Math.ceil(total / Math.max(1, pageSize)))
  const canPrev = page > 1
  const canNext = page < totalPages

  return (
    <Card size="3">
      <Flex direction="column" gap="3">
        <ScrollArea type="auto" scrollbars="horizontal">
          <Table.Root variant="surface">
            <Table.Header>
              <Table.Row>
                {columns.map(col => (
                  <Table.ColumnHeaderCell key={String(col.key)} style={{ width: col.width }}>
                    {col.header}
                  </Table.ColumnHeaderCell>
                ))}
              </Table.Row>
            </Table.Header>

            <Table.Body>
              {loading ? (
                <Table.Row>
                  <Table.Cell colSpan={columns.length}>
                    <Text color="gray">Loading...</Text>
                  </Table.Cell>
                </Table.Row>
              ) : data.length === 0 ? (
                <Table.Row>
                  <Table.Cell colSpan={columns.length}>
                    <Text color="gray">No data</Text>
                  </Table.Cell>
                </Table.Row>
              ) : (
                data.map((row, idx) => (
                  <Table.Row key={idx}>
                    {columns.map(col => (
                      <Table.Cell key={String(col.key)}>
                        {col.render ? col.render(row) : String(row[col.key as keyof T] ?? '')}
                      </Table.Cell>
                    ))}
                  </Table.Row>
                ))
              )}
            </Table.Body>
          </Table.Root>
        </ScrollArea>

        <Flex align="center" justify="between">
          <Text size="2" color="gray">
            Page {page} of {totalPages} • {total} items
          </Text>

          <Flex align="center" gap="2">
            <button
              type="button"
              disabled={!canPrev}
              onClick={() => canPrev && onPageChange?.(page - 1)}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: 6,
                padding: '6px 10px',
                borderRadius: 6,
                border: '1px solid var(--gray-6)',
                background: 'var(--color-panel-solid)',
                color: 'var(--gray-12)',
                opacity: canPrev ? 1 : 0.5,
                cursor: canPrev ? 'pointer' : 'not-allowed',
              }}
            >
              <ChevronLeftIcon /> Prev
            </button>

            <button
              type="button"
              disabled={!canNext}
              onClick={() => canNext && onPageChange?.(page + 1)}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: 6,
                padding: '6px 10px',
                borderRadius: 6,
                border: '1px solid var(--gray-6)',
                background: 'var(--color-panel-solid)',
                color: 'var(--gray-12)',
                opacity: canNext ? 1 : 0.5,
                cursor: canNext ? 'pointer' : 'not-allowed',
              }}
            >
              Next <ChevronRightIcon />
            </button>

            <select
              value={pageSize}
              onChange={e => onPageSizeChange?.(Number(e.target.value))}
              style={{
                padding: '6px 10px',
                borderRadius: 6,
                border: '1px solid var(--gray-6)',
                background: 'var(--color-panel-solid)',
                color: 'var(--gray-12)',
              }}
            >
              {[10, 20, 50, 100].map(size => (
                <option key={size} value={size}>
                  {size} / page
                </option>
              ))}
            </select>
          </Flex>
        </Flex>
      </Flex>
    </Card>
  )
}