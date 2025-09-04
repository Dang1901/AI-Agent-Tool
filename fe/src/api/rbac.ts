// src/api/rbac.ts
import { api } from './client'

// Types
export interface Role {
  id: number
  name: string
  display_name: string
  description?: string
  is_active: boolean
  is_system: boolean
  created_at: string
  updated_at: string
}

export interface Permission {
  id: number
  name: string
  display_name: string
  description?: string
  resource: string
  action: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Resource {
  id: number
  name: string
  display_name: string
  description?: string
  resource_type: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface RoleWithPermissions extends Role {
  permissions: Permission[]
}

export interface UserWithRoles {
  id: number
  email: string
  name?: string
  is_active: boolean
  roles: Role[]
}

// Role APIs
export async function getRoles(skip = 0, limit = 100): Promise<Role[]> {
  const res = await api.get<Role[]>('/rbac/roles', { params: { skip, limit } })
  return res.data
}

export async function getRole(id: number): Promise<RoleWithPermissions> {
  const res = await api.get<RoleWithPermissions>(`/rbac/roles/${id}`)
  return res.data
}

export async function createRole(data: Omit<Role, 'id' | 'created_at' | 'updated_at' | 'is_system'>): Promise<Role> {
  const res = await api.post<Role>('/rbac/roles', data)
  return res.data
}

export async function updateRole(id: number, data: Partial<Role>): Promise<Role> {
  const res = await api.put<Role>(`/rbac/roles/${id}`, data)
  return res.data
}

export async function deleteRole(id: number): Promise<void> {
  await api.delete(`/rbac/roles/${id}`)
}

// Permission APIs
export async function getPermissions(page = 1, pageSize = 100, resource?: string): Promise<Permission[]> {
  const res = await api.get<Permission[]>('/rbac/permissions', { 
    params: { page, page_size: pageSize, resource } 
  })
  return res.data
}

export async function getPermission(id: number): Promise<Permission> {
  const res = await api.get<Permission>(`/rbac/permissions/${id}`)
  return res.data
}

export async function createPermission(data: Omit<Permission, 'id' | 'created_at' | 'updated_at'>): Promise<Permission> {
  const res = await api.post<Permission>('/rbac/permissions', data)
  return res.data
}

export async function updatePermission(id: number, data: Partial<Permission>): Promise<Permission> {
  const res = await api.put<Permission>(`/rbac/permissions/${id}`, data)
  return res.data
}

export async function deletePermission(id: number): Promise<void> {
  await api.delete(`/rbac/permissions/${id}`)
}

// Resource APIs
export async function getResources(skip = 0, limit = 100): Promise<Resource[]> {
  const res = await api.get<Resource[]>('/rbac/resources', { params: { skip, limit } })
  return res.data
}

export async function getResource(id: number): Promise<Resource> {
  const res = await api.get<Resource>(`/rbac/resources/${id}`)
  return res.data
}

export async function createResource(data: Omit<Resource, 'id' | 'created_at' | 'updated_at'>): Promise<Resource> {
  const res = await api.post<Resource>('/rbac/resources', data)
  return res.data
}

export async function updateResource(id: number, data: Partial<Resource>): Promise<Resource> {
  const res = await api.put<Resource>(`/rbac/resources/${id}`, data)
  return res.data
}

export async function deleteResource(id: number): Promise<void> {
  await api.delete(`/rbac/resources/${id}`)
}

// Assignment APIs
export async function assignRolesToUser(userId: number, roleIds: number[]): Promise<void> {
  await api.post(`/rbac/users/${userId}/roles`, { role_ids: roleIds })
}

export async function getUserRoles(userId: number): Promise<Role[]> {
  const res = await api.get<Role[]>(`/rbac/users/${userId}/roles`)
  return res.data
}

export async function getUserPermissions(userId: number): Promise<Permission[]> {
  const res = await api.get<Permission[]>(`/rbac/users/${userId}/permissions`)
  return res.data
}

export async function assignPermissionsToRole(roleId: number, permissionIds: number[]): Promise<void> {
  await api.post(`/rbac/roles/${roleId}/permissions`, { permission_ids: permissionIds })
}

export async function getRolePermissions(roleId: number): Promise<Permission[]> {
  const res = await api.get<Permission[]>(`/rbac/roles/${roleId}/permissions`)
  return res.data
}

// Authorization check
export async function checkUserPermission(userId: number, resource: string, action: string): Promise<{
  user_id: number
  resource: string
  action: string
  has_permission: boolean
}> {
  const res = await api.get(`/rbac/users/${userId}/check-permission`, {
    params: { resource, action }
  })
  return res.data
}
