import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Flex, Card, Spinner, Text, Heading } from '@radix-ui/themes'

export default function LogoutPage() {
  const nav = useNavigate()

  useEffect(() => {
    // Simulate logout process
    setTimeout(() => {
      nav('/login', { replace: true })
    }, 1000)
  }, [nav])

  return (
    <Flex align="center" justify="center" style={{ minHeight: '100vh' }}>
      <Card size="3">
        <Flex direction="column" align="center" gap="3">
          <Spinner size="3" />
          <Heading size="4">Đang đăng xuất</Heading>
          <Text size="2" color="gray">Vui lòng chờ trong giây lát…</Text>
        </Flex>
      </Card>
    </Flex>
  )
}
