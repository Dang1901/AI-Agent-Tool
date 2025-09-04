import { useNavigate } from 'react-router-dom'
import { Button, Card, Flex, Heading, Text } from '@radix-ui/themes'

export default function NotFound() {
  const nav = useNavigate()

  return (
    <Flex align="center" justify="center" style={{ height: '100vh', padding: 24 }}>
      <Card size="4" variant="surface" style={{ maxWidth: 520, width: '100%' }}>
        <Flex direction="column" gap="4" align="center">
          <Heading size="9">404</Heading>
          <Text size="3" color="gray">Oops! Page not found.</Text>
          <Button onClick={() => nav('/')}>Go Home</Button>
        </Flex>
      </Card>
    </Flex>
  )
}
