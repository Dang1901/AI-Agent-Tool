// src/api/auth.ts
import { api, setAccessToken } from './client'

// Payload + response type
export interface LoginPayload {
  email: string
  password: string
}

export interface TokenResponse {
  access_token: string
  token_type?: string
}

export interface UserProfile {
  id: number
  email: string
}

// Đăng nhập: nhận access_token từ BE, lưu vào memory
export async function loginApi(payload: LoginPayload): Promise<UserProfile> {
  const res = await api.post<TokenResponse>('/auth/login', payload)

  const token = res.data?.access_token
  if (!token) throw new Error('Login failed: No token received')

  // Set access token vào memory
  setAccessToken(token)

  // Gọi tiếp /auth/me để lấy thông tin user
  const user = await meApi()
  return user
}

// Đăng ký tài khoản mới
export async function registerApi(payload: LoginPayload): Promise<UserProfile> {
  const res = await api.post<UserProfile>('/auth/register', payload)
  return res.data
}

// Gọi để lấy user hiện tại (sau khi đã login hoặc refresh)
export async function meApi(): Promise<UserProfile> {
  const res = await api.get<UserProfile>('/auth/me')
  return res.data
}

// Đăng xuất: xóa cookie refresh + access_token in memory
export async function logoutApi(): Promise<void> {
  await api.post('/auth/logout', {})
  setAccessToken(null)
}

// Gọi refresh token để lấy access_token mới
export async function refreshTokenApi(): Promise<string> {
  const res = await api.post<TokenResponse>('/auth/refresh', {}, { withCredentials: true })
  const token = res.data?.access_token
  if (!token) throw new Error('Refresh failed: No token received')
  setAccessToken(token)
  return token
}
