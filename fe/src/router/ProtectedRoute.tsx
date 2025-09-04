import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useSelector } from 'react-redux'
import type { RootState } from '@store/rootReducer'

export default function ProtectedRoute() {
  const isAuth = useSelector((s: RootState) => s.auth.isAuthenticated)
  const loc = useLocation()
  if (!isAuth) return <Navigate to="/login" replace state={{ from: loc }} />
  return <Outlet />
}
