// src/router/index.tsx
import { createBrowserRouter, Navigate } from 'react-router-dom'
import ProtectedRoute from './ProtectedRoute'
import Layout from '../layouts/Layout'
import NotFound from '@pages/NotFound'
import LoginPage from '@pages/auth/LoginPage/LoginPage'
import RegisterPage from '@pages/auth/RegisterPage/RegisterPage'
import OverviewPage from '@pages/overview/OverviewPage'
import UserMnt from '@pages/iam/user/ListUserMnt/UserMnt'
import UserDetail from '@pages/iam/user/DetailUser'
import CreatePermissionUser from '@pages/iam/user/DetailUser/src/PermissionUser/CreatePermissionUser/CreatePermissionUser'
import EditPermissionUser from '@pages/iam/user/DetailUser/src/PermissionUser/EditPermissionUser'
import ListFeatures from '@pages/iam/feature/ListFeatures/ListFeature'
import ListRoles from '@pages/iam/role/ListRoles'
import ListPermissions from '@pages/iam/permission/ListPermissions'
import ListPolicies from '@pages/iam/policy/ListPolicies'
import ListUsers from '@pages/iam/user/ListUsers/ListUsers'

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
          
          // IAM - User Management
          { path: 'iam/users', element: <ListUsers /> },
          { path: 'iam/users/management', element: <UserMnt /> },
          { path: 'iam/users/:id', element: <UserDetail /> },
          { path: 'iam/users/:id/permission/create', element: <CreatePermissionUser /> },
          { path: 'iam/users/:id/permission/edit', element: <EditPermissionUser /> },

          // IAM - Role Management
          { path: 'iam/roles', element: <ListRoles /> },

          // IAM - Permission Management
          { path: 'iam/permissions', element: <ListPermissions /> },

          // IAM - Policy Management
          { path: 'iam/policies', element: <ListPolicies /> },

          // Feature Management
          { path: 'iam/features', element: <ListFeatures/> },
        ],
      },
    ],
  },
  { path: '*', element: <NotFound /> },
]);
