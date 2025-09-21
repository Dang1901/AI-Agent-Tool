// src/router/index.tsx
import { createBrowserRouter, Navigate } from 'react-router-dom'
import ProtectedRoute from './ProtectedRoute'
import Layout from '../layouts/Layout'
import NotFound from '@pages/NotFound'
import LoginPage from '@pages/auth/LoginPage/LoginPage'
import RegisterPage from '@pages/auth/RegisterPage/RegisterPage'
import OverviewPage from '@pages/overview/OverviewPage'
import EnvVarsPage from '@pages/envvars/EnvVarsPage'
import ReleasesPage from '@pages/releases/ReleasesPage'
import AuditPage from '@pages/audit/AuditPage'
import LogsPage from '@pages/logs/LogsPage'

export const router = createBrowserRouter([
  { path: '/login', element: <LoginPage /> },
  { path: '/register', element: <RegisterPage /> },
  {
    path: '/',
    element: <ProtectedRoute />,
    children: [
      {
        element: <Layout />,
        children: [
          { index: true, element: <Navigate to="overview" replace /> },
          { path: 'overview', element: <OverviewPage /> },
          { path: 'envvars', element: <EnvVarsPage /> },
          { path: 'releases', element: <ReleasesPage /> },
          { path: 'audit', element: <AuditPage /> },
          { path: 'logs', element: <LogsPage /> },
        ],
      },
    ],
  },
  { path: '*', element: <NotFound /> },
]);
