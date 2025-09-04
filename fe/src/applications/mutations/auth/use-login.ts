import { useMutation, useQueryClient } from '@tanstack/react-query'
import { loginApi, logoutApi } from '@api/auth'
import { useDispatch } from 'react-redux'
import { setSession, clearSession } from '@store/slice'

// Hook login
export function useLogin() {
  const dispatch = useDispatch()
  const qc = useQueryClient()

  return useMutation({
    mutationFn: loginApi,
    onSuccess: (user) => {
      dispatch(setSession({ user }))
      qc.invalidateQueries({ queryKey: ['me'] })
    },
  })
}

// Hook logout
export function useLogout() {
  const dispatch = useDispatch()
  const qc = useQueryClient()

  return useMutation({
    mutationFn: logoutApi,
    onSuccess: () => {
      dispatch(clearSession())
      qc.clear()
    },
  })
}

