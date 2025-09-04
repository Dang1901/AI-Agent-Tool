// src/features/auth/useRegister.ts
import { useMutation } from '@tanstack/react-query'
import { registerApi } from '@api/auth'
import { useDispatch } from 'react-redux'
import { setSession } from '@store/slice'

// Đăng ký: sau khi đăng ký thành công thì lưu user vào Redux
export function useRegister() {
  const dispatch = useDispatch()

  return useMutation({
    mutationFn: registerApi,
    onSuccess: (user) => {
      dispatch(setSession({ user }))
    },
  })
}
