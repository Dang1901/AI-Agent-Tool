// src/applications/queries/abac.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  getPolicies, getPolicy, createPolicy, updatePolicy, deletePolicy,
  assignPolicy, getPolicyAssignments, getUserPolicies, removePolicyAssignment,
  getAttributes, getAttribute, createAttribute,
  setUserAttribute, getUserAttributes, getUserAttributeValue,
  setResourceAttribute, getResourceAttributes,
  authorizeRequest, getAccessLogs
} from '@api/abac'

// Policy queries
export function usePolicies(page = 1, pageSize = 100, activeOnly = false) {
  return useQuery({
    queryKey: ['policies', page, pageSize, activeOnly],
    queryFn: () => getPolicies(page, pageSize, activeOnly),
  })
}

export function usePolicy(id: number) {
  return useQuery({
    queryKey: ['policy', id],
    queryFn: () => getPolicy(id),
    enabled: !!id,
  })
}

export function useCreatePolicy() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: createPolicy,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['policies'] })
    },
  })
}

export function useUpdatePolicy() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) => updatePolicy(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['policies'] })
      queryClient.invalidateQueries({ queryKey: ['policy', id] })
    },
  })
}

export function useDeletePolicy() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: deletePolicy,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['policies'] })
    },
  })
}

// Policy Assignment queries
export function usePolicyAssignments(policyId: number) {
  return useQuery({
    queryKey: ['policy-assignments', policyId],
    queryFn: () => getPolicyAssignments(policyId),
    enabled: !!policyId,
  })
}

export function useUserPolicies(userId: number) {
  return useQuery({
    queryKey: ['user-policies', userId],
    queryFn: () => getUserPolicies(userId),
    enabled: !!userId,
  })
}

export function useAssignPolicy() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: assignPolicy,
    onSuccess: (_, data) => {
      queryClient.invalidateQueries({ queryKey: ['policy-assignments', data.policy_id] })
      if (data.assignment_type === 'user') {
        queryClient.invalidateQueries({ queryKey: ['user-policies', data.assignment_id] })
      }
    },
  })
}

export function useRemovePolicyAssignment() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: removePolicyAssignment,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['policy-assignments'] })
    },
  })
}

// Attribute queries
export function useAttributes(skip = 0, limit = 100, dataType?: string) {
  return useQuery({
    queryKey: ['attributes', skip, limit, dataType],
    queryFn: () => getAttributes(skip, limit, dataType),
  })
}

export function useAttribute(id: number) {
  return useQuery({
    queryKey: ['attribute', id],
    queryFn: () => getAttribute(id),
    enabled: !!id,
  })
}

export function useCreateAttribute() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: createAttribute,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['attributes'] })
    },
  })
}

// User Attribute queries
export function useUserAttributes(userId: number) {
  return useQuery({
    queryKey: ['user-attributes', userId],
    queryFn: () => getUserAttributes(userId),
    enabled: !!userId,
  })
}

export function useUserAttributeValue(userId: number, attributeName: string) {
  return useQuery({
    queryKey: ['user-attribute-value', userId, attributeName],
    queryFn: () => getUserAttributeValue(userId, attributeName),
    enabled: !!userId && !!attributeName,
  })
}

export function useSetUserAttribute() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ userId, attributeName, value }: { userId: number; attributeName: string; value: string }) => 
      setUserAttribute(userId, attributeName, value),
    onSuccess: (_, { userId }) => {
      queryClient.invalidateQueries({ queryKey: ['user-attributes', userId] })
      queryClient.invalidateQueries({ queryKey: ['user-attribute-value', userId] })
    },
  })
}

// Resource Attribute queries
export function useResourceAttributes(resourceId: number, resourceType: string) {
  return useQuery({
    queryKey: ['resource-attributes', resourceId, resourceType],
    queryFn: () => getResourceAttributes(resourceId, resourceType),
    enabled: !!resourceId && !!resourceType,
  })
}

export function useSetResourceAttribute() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ resourceId, resourceType, attributeName, value }: { 
      resourceId: number; 
      resourceType: string; 
      attributeName: string; 
      value: string 
    }) => setResourceAttribute(resourceId, resourceType, attributeName, value),
    onSuccess: (_, { resourceId, resourceType }) => {
      queryClient.invalidateQueries({ queryKey: ['resource-attributes', resourceId, resourceType] })
    },
  })
}

// Authorization query
export function useAuthorizeRequest() {
  return useMutation({
    mutationFn: authorizeRequest,
  })
}

// Access Log queries
export function useAccessLogs(userId?: number, skip = 0, limit = 100) {
  return useQuery({
    queryKey: ['access-logs', userId, skip, limit],
    queryFn: () => getAccessLogs(userId, skip, limit),
  })
}
