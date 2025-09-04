import { Outlet, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { Box, Button, Flex, Heading } from '@radix-ui/themes'
import { ExitIcon, HamburgerMenuIcon } from '@radix-ui/react-icons'
import { useLogout } from '@applications/mutations/auth'
import Sidebar from './Sidebar'

export default function DashboardLayout() {
  const nav = useNavigate()
  const logout = useLogout()
  const [collapsed, setCollapsed] = useState(false)

  const handleLogout = async () => {
    try {
      await logout.mutateAsync()
      nav('/login')
    } catch {
      // noop
    }
  }

  return (
    <Flex direction="column" style={{ height: '100vh' }}>
      {/* Top Navbar spans full width */}
      <Flex
        align="center"
        justify="between"
        style={{
          height: 56,
          padding: '0 16px',
          background: '#18244b',
          color: 'white',
          flexShrink: 0,
        }}
      >
        <Flex align="center" gap="3">
          <Button variant="ghost" color="gray" onClick={() => setCollapsed(v => !v)} aria-label="Toggle sidebar">
            <HamburgerMenuIcon color="white" />
          </Button>
          <Flex align="center" gap="2" style={{ minWidth: 0 }}>
          <Heading
            size="4"
            // style={{
            //   opacity: collapsed ? 0 : 1,
            //   transition: 'opacity 200ms ease',
            //   overflow: 'hidden',
            //   whiteSpace: 'nowrap',
            //   width: collapsed ? 0 : 'auto',
            // }}
          >
            MY APP 
          </Heading>
        </Flex>
        </Flex>

        <Flex align="center" gap="3">
          <Button variant="surface" onClick={handleLogout}>
            <ExitIcon /> Account
          </Button>
        </Flex>
      </Flex>

      {/* Content row: sidebar below header */}
      <Flex style={{ flex: 1, minHeight: 0 }}>
        <Sidebar collapsed={collapsed} />
        <Box style={{ flex: 1, minWidth: 0, padding: 24, overflow: 'auto' }}>
          <Outlet />
        </Box>
      </Flex>
    </Flex>
  )
}


