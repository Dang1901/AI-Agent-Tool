import {
  Card,
  Text,
  TextField,
  Flex,
  Heading,
  Button,
  Separator,
  Callout,
} from '@radix-ui/themes'
import { useForm } from 'react-hook-form'
import { useNavigate } from 'react-router-dom'
import { useLogin } from '@applications/mutations/auth'
import './LoginPage.css'

type FormValues = {
  email: string
  password: string
}
type ApiError = { 
  response?: { 
    data?: { 
      detail?: string | Array<{ type: string; loc: string[]; msg: string; input: any; url: string }>
    } 
  } 
}

const LoginPage = () => {
  const nav = useNavigate()
  const loginMutation = useLogin()

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormValues>({
    defaultValues: { email: '', password: '' },
    mode: 'onSubmit',
  })

  const onSubmit = async (values: FormValues) => {
    try {
      await loginMutation.mutateAsync(values)
      nav('/')
    } catch (error) {
      console.log('Login error:', error)
    }
  }

  return (
      <div className="login-background">
        <Card className="login-card" size="4">
          <Flex direction="column" gap="5">
            <Heading size="6">Sign in</Heading>

            {loginMutation.isError && (
              <Callout.Root color="red" role="alert">
                <Callout.Text>
                  {(() => {
                    const error = loginMutation.error as ApiError
                    const detail = error?.response?.data?.detail
                    
                    if (typeof detail === 'string') {
                      return detail
                    } else if (Array.isArray(detail)) {
                      return detail.map(err => err.msg).join(', ')
                    } else if (detail && typeof detail === 'object') {
                      return JSON.stringify(detail)
                    } else {
                      return 'Login failed. Please try again.'
                    }
                  })()}
                </Callout.Text>
              </Callout.Root>
            )}

            <form onSubmit={handleSubmit(onSubmit)}>
              <Flex direction="column" gap="4">
                {/* Email */}
                <div>
                  <Text as="label" size="2">
                    Email
                  </Text>
                  <TextField.Root
                    placeholder="Enter your email address"
                    {...register('email', {
                      required: 'Please enter email',
                    })}
                  />
                  {errors.email && (
                    <Text size="1" color="red">
                      {errors.email.message}
                    </Text>
                  )}
                </div>

                {/* Password */}
                <div>
                  <Flex justify="between" align="center">
                    <Text as="label" size="2">
                      Password
                    </Text>
                    <Text asChild size="1">
                      <a
                        href="#"
                        style={{
                          color: '#3b82f6',
                          textDecoration: 'underline',
                        }}
                      >
                        Forgot password?
                      </a>
                    </Text>
                  </Flex>
                  <TextField.Root
                    type="password"
                    placeholder="Enter your password"
                    {...register('password', {
                      required: 'Please enter password',
                    })}
                  />
                  {errors.password && (
                    <Text size="1" color="red">
                      {errors.password.message}
                    </Text>
                  )}
                </div>

                <Flex justify="end" gap="3" mt="4">
                  <Button variant="soft" type="button" onClick={() => nav('/register')}>
                    Create an account
                  </Button>
                  <Button
                    type="submit"
                    style={{
                      background: 'linear-gradient(to right, #2563eb, #3b82f6)',
                      color: 'white',
                    }}
                  >
                    Sign in
                  </Button>
                </Flex>
              </Flex>
            </form>

            <Separator size="4" />
          </Flex>
        </Card>
      </div>
  )
}

export default LoginPage
