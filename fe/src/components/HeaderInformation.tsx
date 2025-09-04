import { Card, Flex, Heading, Tabs, Text } from '@radix-ui/themes'
import type { ReactNode } from 'react'
import { Link, useNavigate } from 'react-router-dom'

type BreadcrumbItem = { label: string; to?: string }
type TabItem = { key: string; label: string; to?: string }

type HeaderInformationProps = {
  breadcrumb?: ReactNode
  breadcrumbs?: BreadcrumbItem[]
  title: string
  description?: string
  action?: ReactNode
  icon?: ReactNode
  tabs?: TabItem[]
  activeTabKey?: string
  onTabChange?: (key: string) => void
}

export default function HeaderInformation({ breadcrumb, breadcrumbs, title, description, action, icon, tabs, activeTabKey, onTabChange }: HeaderInformationProps) {
  const navigate = useNavigate()
  return (
    <Card variant="surface" size="3" style={{ marginBottom: 16 }}>
      <Flex align="center" justify="between">
        <Flex direction="column" gap="2" style={{ minWidth: 0 }}>
          {breadcrumbs && breadcrumbs.length > 0 ? (
            <Flex align="center" gap="2" wrap="wrap">
              {breadcrumbs.map((bc, idx) => (
                <Flex key={`${bc.label}-${idx}`} align="center" gap="2">
                  {bc.to ? (
                    <Text asChild size="2" weight="bold">
                      <Link to={bc.to} style={{ color: 'gray', textDecoration: 'none' }}>{bc.label}</Link>
                    </Text>
                  ) : (
                    <Text size="2" weight="bold" color="indigo">{bc.label}</Text>
                  )}
                  {idx < breadcrumbs.length - 1 && <Text size="5" color="gray">›</Text>}
                </Flex>
              ))}
            </Flex>
          ) : (
            breadcrumb && (
              <Text size="2" color="indigo" weight="bold">
                {breadcrumb}
              </Text>
            )
          )}
          <Flex align="center" gap="3">
            {icon}
            <Heading size="5" style={{ margin: 0 }}>
              {title}
            </Heading>
          </Flex>
          {description && (
            <Text size="2" color="gray">
              {description}
            </Text>
          )}
        </Flex>

        {action}
      </Flex>

      {tabs && tabs.length > 0 && (
        <Tabs.Root
          value={activeTabKey}
          onValueChange={(v) => {
            if (onTabChange) onTabChange(v)
            else {
              const tab = tabs.find(t => t.key === v)
              if (tab?.to) navigate(tab.to)
            }
          }}
        >
          <Tabs.List>
            {tabs.map(t => (
              <Tabs.Trigger key={t.key} value={t.key}>{t.label}</Tabs.Trigger>
            ))}
          </Tabs.List>
        </Tabs.Root>
      )}
    </Card>
  )
}


