import {
  Card,
  Flex,
  Text,
  Heading,
  Button,
  TextField,
  Separator,
  Callout,
  Theme,
} from '@radix-ui/themes'
import { PersonIcon } from '@radix-ui/react-icons'
import { useForm } from 'react-hook-form'
import { useRegister } from '@applications/mutations/auth'
import { useSelector } from 'react-redux'
import { useEffect } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import type { RootState } from '@store/rootReducer'

import './RegisterPage.css'

type FormValues = {
  email: string
  password: string
  name: string
}
type LocationState = { from?: { pathname: string } }
type ApiError = { response?: { data?: { detail?: string } } }

const RegisterPage = () => {
  const isAuth = useSelector((s: RootState) => s.auth.isAuthenticated)
  const nav = useNavigate()
  const loc = useLocation() as unknown as { state?: LocationState }

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormValues>({
    defaultValues: { email: '', password: '', name: '' },
    mode: 'onSubmit',
  })

  const registerMutation = useRegister()

  useEffect(() => {
    if (isAuth) {
      const redirect = loc.state?.from?.pathname || '/'
      nav(redirect, { replace: true })
    }
  }, [isAuth])

  const onSubmit = async (values: FormValues) => {
    try {
      await registerMutation.mutateAsync(values)
      nav('/login', { replace: true })
    } catch {
      console.log(errors);
    }
  }

  return (
    <Theme appearance="dark">
      <div className="register-background">
        <Card className="register-card" size="4">
          <Flex direction="column" gap="5">
            <Flex align="center" gap="2">
              <PersonIcon />
              <Heading size="6">Create an account</Heading>
            </Flex>

            {registerMutation.isError && (
              <Callout.Root color="red" role="alert">
                <Callout.Text>
                  {(registerMutation.error as ApiError)?.response?.data?.detail ||
                    'Registration failed. Please try again.'}
                </Callout.Text>
              </Callout.Root>
            )}

            <form onSubmit={handleSubmit(onSubmit)}>
              <Flex direction="column" gap="4">
                {/* Full Name */}
                <div>
                  <Text as="label" size="2">
                    Full name
                  </Text>
                  <TextField.Root
                    placeholder="Nguyễn Văn A"
                    {...register('name', { required: 'Please enter your name' })}
                  />
                  {errors.name && (
                    <Text size="1" color="red">
                      {errors.name.message}
                    </Text>
                  )}
                </div>

                {/* Email */}
                <div>
                  <Text as="label" size="2">
                    Email
                  </Text>
                  <TextField.Root
                    placeholder="Enter your email address"
                    {...register('email', {
                      required: 'Please enter email',
                      pattern: {
                        value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                        message: 'Invalid email address',
                      },
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
                  <Text as="label" size="2">
                    Password
                  </Text>
                  <TextField.Root
                    type="password"
                    placeholder="Enter your password"
                    {...register('password', {
                      required: 'Please enter password',
                      minLength: { value: 6, message: 'At least 6 characters' },
                    })}
                  />
                  {errors.password && (
                    <Text size="1" color="red">
                      {errors.password.message}
                    </Text>
                  )}
                </div>

                {/* Actions */}
                <Flex justify="end" gap="3" mt="4">
                  <Button
                    type="button"
                    variant="soft"
                    onClick={() => nav('/login')}
                  >
                    Back to sign in
                  </Button>
                  <Button
                    type="submit"
                    disabled={registerMutation.isPending}
                    style={{
                      background: 'linear-gradient(to right, #2563eb, #3b82f6)',
                      color: 'white',
                    }}
                  >
                    {registerMutation.isPending
                      ? 'Creating…'
                      : 'Create account'}
                  </Button>
                </Flex>
              </Flex>
            </form>

            <Separator size="4" />
            <Text size="1" color="gray">
              Use a strong password. You can change later.
            </Text>
          </Flex>
        </Card>
      </div>
    </Theme>

  )
}

export default RegisterPage
