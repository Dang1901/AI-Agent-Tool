// src/applications/queries/rbac.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  getRoles, getRole, createRole, updateRole, deleteRole,
  getPermissions, getPermission, createPermission, updatePermission, deletePermission,
  getResources, getResource, createResource, updateResource, deleteResource,
  assignRolesToUser, getUserRoles, getUserPermissions,
  assignPermissionsToRole, getRolePermissions, checkUserPermission
} from '@api/rbac'

// Role queries
export function useRoles(skip = 0, limit = 100) {
  return useQuery({
    queryKey: ['roles', skip, limit],
    queryFn: () => getRoles(skip, limit),
  })
}

export function useRole(id: number) {
  return useQuery({
    queryKey: ['role', id],
    queryFn: () => getRole(id),
    enabled: !!id,
  })
}

export function useCreateRole() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: createRole,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['roles'] })
    },
  })
}

export function useUpdateRole() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) => updateRole(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['roles'] })
      queryClient.invalidateQueries({ queryKey: ['role', id] })
    },
  })
}

export function useDeleteRole() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: deleteRole,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['roles'] })
    },
  })
}

// Permission queries
export function usePermissions(page = 1, pageSize = 100, resource?: string) {
  return useQuery({
    queryKey: ['permissions', page, pageSize, resource],
    queryFn: () => getPermissions(page, pageSize, resource),
  })
}

export function usePermission(id: number) {
  return useQuery({
    queryKey: ['permission', id],
    queryFn: () => getPermission(id),
    enabled: !!id,
  })
}

export function useCreatePermission() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: createPermission,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['permissions'] })
    },
  })
}

export function useUpdatePermission() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) => updatePermission(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['permissions'] })
      queryClient.invalidateQueries({ queryKey: ['permission', id] })
    },
  })
}

export function useDeletePermission() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: deletePermission,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['permissions'] })
    },
  })
}

// Resource queries
export function useResources(skip = 0, limit = 100) {
  return useQuery({
    queryKey: ['resources', skip, limit],
    queryFn: () => getResources(skip, limit),
  })
}

export function useResource(id: number) {
  return useQuery({
    queryKey: ['resource', id],
    queryFn: () => getResource(id),
    enabled: !!id,
  })
}

export function useCreateResource() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: createResource,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['resources'] })
    },
  })
}

export function useUpdateResource() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) => updateResource(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['resources'] })
      queryClient.invalidateQueries({ queryKey: ['resource', id] })
    },
  })
}

export function useDeleteResource() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: deleteResource,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['resources'] })
    },
  })
}

// Assignment queries
export function useUserRoles(userId: number) {
  return useQuery({
    queryKey: ['user-roles', userId],
    queryFn: () => getUserRoles(userId),
    enabled: !!userId,
  })
}

export function useUserPermissions(userId: number) {
  return useQuery({
    queryKey: ['user-permissions', userId],
    queryFn: () => getUserPermissions(userId),
    enabled: !!userId,
  })
}

export function useRolePermissions(roleId: number) {
  return useQuery({
    queryKey: ['role-permissions', roleId],
    queryFn: () => getRolePermissions(roleId),
    enabled: !!roleId,
  })
}

export function useAssignRolesToUser() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ userId, roleIds }: { userId: number; roleIds: number[] }) => 
      assignRolesToUser(userId, roleIds),
    onSuccess: (_, { userId }) => {
      queryClient.invalidateQueries({ queryKey: ['user-roles', userId] })
      queryClient.invalidateQueries({ queryKey: ['user-permissions', userId] })
    },
  })
}

export function useAssignPermissionsToRole() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ roleId, permissionIds }: { roleId: number; permissionIds: number[] }) => 
      assignPermissionsToRole(roleId, permissionIds),
    onSuccess: (_, { roleId }) => {
      queryClient.invalidateQueries({ queryKey: ['role-permissions', roleId] })
      queryClient.invalidateQueries({ queryKey: ['role', roleId] })
    },
  })
}

// Authorization check
export function useCheckUserPermission(userId: number, resource: string, action: string) {
  return useQuery({
    queryKey: ['check-permission', userId, resource, action],
    queryFn: () => checkUserPermission(userId, resource, action),
    enabled: !!userId && !!resource && !!action,
  })
}
