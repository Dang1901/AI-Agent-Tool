import { NavLink } from 'react-router-dom'
import { Box, Flex, Text } from '@radix-ui/themes'
import { DashboardIcon, PersonIcon, ChevronDownIcon } from '@radix-ui/react-icons'

type SidebarProps = {
  collapsed: boolean
}

export default function Sidebar({ collapsed }: SidebarProps) {
  type NavItem = {
    label: string
    to?: string
    icon?: React.ComponentType<{ className?: string }>
    children?: Array<{ label: string; to: string , icon?: React.ComponentType<{ className?: string }> }>
  }

  const groups: Array<{ title: string; items: NavItem[] }> = [
    {
      title: 'Administration overview',
      items: [
        { label: 'Dashboard Overview', to: '/overview', icon: DashboardIcon },
        {
          label: 'IAM',
          to: '/iam',
          icon: PersonIcon,
          children: [
            { label: 'Users', to: '/users' },
            { label: 'Roles', to: '/roles' },
            { label: 'Permissions', to: '/permissions' },
            { label: 'Policies', to: '/policies' },
            { label: 'Features', to: '/features' },
          ],
        },
      ],
    },
  ] as const

  return (
    <Box
      style={{
        width: collapsed ? 0 : 260,
        borderRight: collapsed ? 'none' : '1px solid var(--gray-5)',
        padding: 0,
        display: 'flex',
        flexDirection: 'column',
        transition: 'width 240ms cubic-bezier(.2,.8,.2,1)',
        overflow: 'hidden',
        pointerEvents: collapsed ? 'none' : 'auto',
      }}
      aria-hidden={collapsed}
    >

      {!collapsed && (
        <Box style={{ padding: 12, overflow: 'auto', transition: 'padding 200ms ease' }}>
          {groups.map(group => (
          <Box key={group.title} style={{ marginBottom: 12 }}>
            <Text
              size="1"
              color="gray"
              style={{
                textTransform: 'uppercase',
                letterSpacing: 0.5,
                opacity: 1,
                transition: 'opacity 200ms ease',
              }}
            >
              {group.title}
            </Text>
            <Flex direction="column" gap="1" style={{ marginTop: 8 }}>
              {group.items.map(Item => {
                const hasChildren = !!Item.children && Item.children.length > 0
                return (
                  <Box key={Item.label}>
                    {hasChildren ? (
                      <details>
                        <summary style={{ listStyle: 'none' }}>
                          <Flex
                            align="center"
                            style={{
                              gap: 8,
                              padding: '8px 10px',
                              borderRadius: 6,
                              cursor: 'pointer',
                              color: 'var(--gray-11)'
                            }}
                          >
                            {Item.icon && <Item.icon />}
                            <span>{Item.label}</span>
                            <ChevronDownIcon style={{ marginLeft: 'auto' }} />
                          </Flex>
                        </summary>
                        <Flex direction="column" gap="1" style={{ marginTop: 6, marginLeft: 26 }}>
                          {Item.children!.map(child => {
                            const base = Item.to || ''
                            const childPath = child.to || ''
                            const fullTo = base
                              ? `${base.replace(/\/$/, '')}/${childPath.replace(/^\//, '')}`
                              : childPath
                            return (
                              <NavLink
                                key={fullTo}
                                to={fullTo}
                                style={({ isActive }) => ({
                                  display: 'flex',
                                  alignItems: 'center',
                                  gap: 8,
                                  padding: '6px 8px',
                                  borderRadius: 6,
                                  color: isActive ? 'var(--accent-11)' : 'var(--gray-11)',
                                  background: isActive ? 'var(--accent-a3)' : 'transparent',
                                  textDecoration: 'none',
                                  fontWeight: isActive ? 600 : 500,
                                })}
                              >
                                {child.icon && <child.icon />}
                                <span>{child.label}</span>
                              </NavLink>
                            )
                          })}
                        </Flex>
                      </details>
                    ) : (
                      <NavLink
                        to={Item.to!}
                        style={({ isActive }) => ({
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'flex-start',
                          gap: 8,
                          padding: '8px 10px',
                          borderRadius: 6,
                          color: isActive ? 'var(--accent-11)' : 'var(--gray-11)',
                          background: isActive ? 'var(--accent-a3)' : 'transparent',
                          textDecoration: 'none',
                          fontWeight: isActive ? 600 : 500,
                          transition: 'background-color 160ms ease, color 160ms ease, padding 200ms ease',
                        })}
                      >
                        {Item.icon && <Item.icon />}
                        <span>{Item.label}</span>
                      </NavLink>
                    )}
                  </Box>
                )
              })}
            </Flex>
          </Box>
          ))}
        </Box>
      )}
    </Box>
  )
}


