// src/api/abac.ts
import { api } from './client'

// Types
export interface Policy {
  id: number
  name: string
  description?: string
  policy_type: string
  priority: number
  is_active: boolean
  subject_conditions?: Record<string, any>
  resource_conditions?: Record<string, any>
  action_conditions?: Record<string, any>
  environment_conditions?: Record<string, any>
  effect: string
  obligations?: Record<string, any>
  created_at: string
  updated_at: string
}

export interface PolicyAssignment {
  id: number
  policy_id: number
  assignment_type: string
  assignment_id?: number
  assignment_name?: string
  is_active: boolean
  created_at: string
}

export interface Attribute {
  id: number
  name: string
  display_name: string
  description?: string
  attribute_type: string
  data_type: string
  is_required: boolean
  is_multivalued: boolean
  allowed_values?: string[]
  default_value?: string
  created_at: string
  updated_at: string
}

export interface UserAttribute {
  id: number
  user_id: number
  attribute_id: number
  value: string
  created_at: string
  updated_at: string
  attribute: Attribute
}

export interface ResourceAttribute {
  id: number
  resource_id: number
  resource_type: string
  attribute_id: number
  value: string
  created_at: string
  updated_at: string
  attribute: Attribute
}

export interface AccessLog {
  id: number
  user_id?: number
  resource_type: string
  resource_id?: number
  action: string
  decision: string
  policy_id?: number
  context?: Record<string, any>
  ip_address?: string
  user_agent?: string
  created_at: string
}

export interface AuthorizationRequest {
  user_id: number
  resource_type: string
  resource_id?: number
  action: string
  context?: Record<string, any>
}

export interface AuthorizationResponse {
  decision: string
  policy_id?: number
  reason?: string
  obligations?: Record<string, any>
}

// Policy APIs
export async function getPolicies(page = 1, pageSize = 100, activeOnly = false): Promise<Policy[]> {
  const res = await api.get<Policy[]>('/abac/policies', { 
    params: { page, page_size: pageSize, active_only: activeOnly } 
  })
  return res.data
}

export async function getPolicy(id: number): Promise<Policy> {
  const res = await api.get<Policy>(`/abac/policies/${id}`)
  return res.data
}

export async function createPolicy(data: Omit<Policy, 'id' | 'created_at' | 'updated_at'>): Promise<Policy> {
  const res = await api.post<Policy>('/abac/policies', data)
  return res.data
}

export async function updatePolicy(id: number, data: Partial<Policy>): Promise<Policy> {
  const res = await api.put<Policy>(`/abac/policies/${id}`, data)
  return res.data
}

export async function deletePolicy(id: number): Promise<void> {
  await api.delete(`/abac/policies/${id}`)
}

// Policy Assignment APIs
export async function assignPolicy(data: Omit<PolicyAssignment, 'id' | 'created_at'>): Promise<PolicyAssignment> {
  const res = await api.post<PolicyAssignment>('/abac/policy-assignments', data)
  return res.data
}

export async function getPolicyAssignments(policyId: number): Promise<PolicyAssignment[]> {
  const res = await api.get<PolicyAssignment[]>(`/abac/policies/${policyId}/assignments`)
  return res.data
}

export async function getUserPolicies(userId: number): Promise<Policy[]> {
  const res = await api.get<Policy[]>(`/abac/users/${userId}/policies`)
  return res.data
}

export async function removePolicyAssignment(assignmentId: number): Promise<void> {
  await api.delete(`/abac/policy-assignments/${assignmentId}`)
}

// Attribute APIs
export async function getAttributes(skip = 0, limit = 100, dataType?: string): Promise<Attribute[]> {
  const res = await api.get<Attribute[]>('/abac/attributes', { 
    params: { skip, limit, data_type: dataType } 
  })
  return res.data
}

export async function getAttribute(id: number): Promise<Attribute> {
  const res = await api.get<Attribute>(`/abac/attributes/${id}`)
  return res.data
}

export async function createAttribute(data: Omit<Attribute, 'id' | 'created_at' | 'updated_at'>): Promise<Attribute> {
  const res = await api.post<Attribute>('/abac/attributes', data)
  return res.data
}

// User Attribute APIs
export async function setUserAttribute(userId: number, attributeName: string, value: string): Promise<void> {
  await api.post(`/abac/users/${userId}/attributes`, null, {
    params: { attribute_name: attributeName, value }
  })
}

export async function getUserAttributes(userId: number): Promise<UserAttribute[]> {
  const res = await api.get<UserAttribute[]>(`/abac/users/${userId}/attributes`)
  return res.data
}

export async function getUserAttributeValue(userId: number, attributeName: string): Promise<{ attribute_name: string; value: string }> {
  const res = await api.get(`/abac/users/${userId}/attributes/${attributeName}`)
  return res.data
}

// Resource Attribute APIs
export async function setResourceAttribute(
  resourceId: number, 
  resourceType: string, 
  attributeName: string, 
  value: string
): Promise<void> {
  await api.post(`/abac/resources/${resourceId}/attributes`, null, {
    params: { resource_type: resourceType, attribute_name: attributeName, value }
  })
}

export async function getResourceAttributes(resourceId: number, resourceType: string): Promise<ResourceAttribute[]> {
  const res = await api.get<ResourceAttribute[]>(`/abac/resources/${resourceId}/attributes`, {
    params: { resource_type: resourceType }
  })
  return res.data
}

// Authorization API
export async function authorizeRequest(request: AuthorizationRequest): Promise<AuthorizationResponse> {
  const res = await api.post<AuthorizationResponse>('/abac/authorize', request)
  return res.data
}

// Access Log APIs
export async function getAccessLogs(userId?: number, skip = 0, limit = 100): Promise<AccessLog[]> {
  const res = await api.get<AccessLog[]>('/abac/access-logs', {
    params: { user_id: userId, skip, limit }
  })
  return res.data
}
