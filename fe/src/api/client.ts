// src/api/client.ts
import { clearSession, setSession } from '@store/slice'
import { store } from '@store/store'
import axios from 'axios'
import { loggerService } from '../services/logger'

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
  const startTime = Date.now();
  (config as { startTime?: number }).startTime = startTime;
  
  // Log request
  loggerService.addLog({
    method: config.method?.toUpperCase() || 'GET',
    url: config.url || '',
    requestData: {
      params: config.params,
      data: config.data,
      headers: config.headers
    },
    type: 'request'
  });

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
  (res) => {
    const requestConfig = res.config as { startTime?: number };
    const duration = requestConfig.startTime ? Date.now() - requestConfig.startTime : undefined;
    
    // Log successful response
    loggerService.addLog({
      method: res.config.method?.toUpperCase() || 'GET',
      url: res.config.url || '',
      status: res.status,
      statusText: res.statusText,
      responseData: {
        data: res.data,
        headers: res.headers
      },
      duration,
      type: 'response'
    });
    
    return res;
  },
  async (error) => {
    const errorConfig = error.config as { startTime?: number; _retry?: boolean };
    const duration = errorConfig?.startTime ? Date.now() - errorConfig.startTime : undefined;
    
    // Log error response
    loggerService.addLog({
      method: error.config?.method?.toUpperCase() || 'UNKNOWN',
      url: error.config?.url || 'UNKNOWN',
      status: error.response?.status,
      statusText: error.response?.statusText,
      responseData: error.response?.data,
      error: error.message,
      duration,
      type: 'error'
    });
    
    const { config: originalConfig, response } = error
    if (response?.status === 401 && !originalConfig._retry) {
      if (refreshing) {
        await new Promise<void>((resolve) => pending.push(resolve))
        originalConfig._retry = true
        return api(originalConfig)
      }
      refreshing = true
      originalConfig._retry = true
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
        return api(originalConfig)
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
