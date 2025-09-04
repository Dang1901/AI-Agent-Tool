// src/pages/Dashboard.tsx
import { Button, Card, Flex, Heading, Text } from '@radix-ui/themes'
import HeaderInformation from '@components/HeaderInformation'
import { DesktopIcon, ReloadIcon } from '@radix-ui/react-icons'
import { useSelector } from 'react-redux'
import type { RootState } from '@store/rootReducer'

export default function OverviewPage() {
  const user = useSelector((s: RootState) => s.auth.user)

  return (
    <Flex direction="column" gap="4">
      <HeaderInformation
        breadcrumb={<Text as="span">Home</Text>}
        title="FMON Administration"
        description="Summary of service packages in system"
        icon={<DesktopIcon />}
        action={<Button><ReloadIcon /> SYNC DATA</Button>}
      />
      <Card size="4">
        <Flex direction="column" gap="2">
          <Heading size="4">Xin chào{user?.name ? `, ${user.name}` : ''} 👋</Heading>
          <Text size="2" color="gray">
            Đây là trang tổng quan. Bạn có thể bắt đầu thêm widget/section theo nhu cầu.
          </Text>
        </Flex>
      </Card>
    </Flex>
  )
}
