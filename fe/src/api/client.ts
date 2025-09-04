// src/api/client.ts
import { clearSession, setSession } from '@store/slice'
import { store } from '@store/store'
import axios from 'axios'

// Token ở memory (không persist)
let ACCESS_TOKEN: string | null = null
export const setAccessToken = (t: string | null) => (ACCESS_TOKEN = t)

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  withCredentials: true, // cần cho cookie httpOnly (refresh)
  timeout: 25_000,
})

// Gắn access token vào header nếu có
api.interceptors.request.use((config) => {
  if (ACCESS_TOKEN) {
    config.headers = config.headers ?? {}
    config.headers.Authorization = `Bearer ${ACCESS_TOKEN}`
  }
  return config
})

// Tự refresh khi 401 (nếu backend có endpoint /auth/refresh)
let refreshing = false
let pending: Array<() => void> = []

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const { config, response } = error
    if (response?.status === 401 && !config._retry) {
      if (refreshing) {
        await new Promise<void>((resolve) => pending.push(resolve))
        config._retry = true
        return api(config)
      }
      refreshing = true
      config._retry = true
      try {
        // gọi refresh — cookie httpOnly sẽ tự gửi kèm
        const r = await axios.post(
          (import.meta.env.VITE_API_BASE_URL || '/api') + '/auth/refresh',
          {},
          { withCredentials: true }
        )
        const newToken = r.data?.access_token as string
        setAccessToken(newToken)
        // (tuỳ chọn) sync lại user
        if (r.data?.user) {
          store.dispatch(setSession({ user: r.data.user }))
        }
        pending.forEach((fn) => fn())
        pending = []
        return api(config)
      } catch (e) {
        setAccessToken(null)
        store.dispatch(clearSession())
        pending = []
        throw e
      } finally {
        refreshing = false
      }
    }
    return Promise.reject(error)
  }
)
