import { api } from "./client"

export interface User {
  id: number
  email: string
  name?: string
  dob?: string
  gender?: string
  phone_number?: string
  avatar_url?: string
  is_verified: boolean
  is_active: boolean
  department?: string
  position?: string
  location?: string
  clearance_level?: string
  created_at: string
  updated_at: string
}

// User APIs - Read only
export async function getUsers(
  page = 1, 
  pageSize = 100, 
  search?: string, 
  isActive?: boolean
): Promise<User[]> {
  const res = await api.get<User[]>('/users', { 
    params: { page, page_size: pageSize, search, is_active: isActive } 
  })
  return res.data
}
