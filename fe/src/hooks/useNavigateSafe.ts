 import { useCallback } from 'react'
import { useNavigate } from 'react-router-dom'

export function useNavigateSafe() {
  const navigate = useNavigate()
  return useCallback(
    (to: string, replace?: boolean) => navigate(to, { replace }),
    [navigate],
  )
}


