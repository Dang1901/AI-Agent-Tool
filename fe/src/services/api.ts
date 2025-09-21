import axios from 'axios'
import { loggerService } from './logger'

// API base configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for auth and logging
apiClient.interceptors.request.use(
  (config) => {
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

    // Add auth token if available
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    // Log request error
    loggerService.addLog({
      method: 'UNKNOWN',
      url: 'UNKNOWN',
      error: error.message,
      type: 'error'
    });
    return Promise.reject(error)
  }
)

// Response interceptor for error handling and logging
apiClient.interceptors.response.use(
  (response) => {
    const requestConfig = response.config as { startTime?: number };
    const duration = requestConfig.startTime ? Date.now() - requestConfig.startTime : undefined;
    
    // Log successful response
    loggerService.addLog({
      method: response.config.method?.toUpperCase() || 'GET',
      url: response.config.url || '',
      status: response.status,
      statusText: response.statusText,
      responseData: {
        data: response.data,
        headers: response.headers
      },
      duration,
      type: 'response'
    });
    
    return response;
  },
  (error) => {
    const errorConfig = error.config as { startTime?: number };
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

    if (error.response?.status === 401) {
      // Handle unauthorized
      localStorage.removeItem('auth_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Environment Variables API
export const envVarApi = {
  // List environment variables
  listEnvVars: async (params: {
    scope_level?: string
    scope_ref_id?: string
    key_filter?: string
    tag_filter?: string
    type_filter?: string
    status_filter?: string
    page?: number
    size?: number
  }) => {
    const response = await apiClient.get('/envvars', { params })
    return response.data
  },

  // Get environment variable by ID
  getEnvVar: async (id: string) => {
    const response = await apiClient.get(`/envvars/${id}`)
    return response.data
  },

  // Create environment variable
  createEnvVar: async (data: {
    key: string
    value: string
    type: string
    scope_level: string
    scope_ref_id: string
    tags: string[]
    description?: string
    is_secret: boolean
    created_by: string
  }) => {
    const response = await apiClient.post('/envvars', data)
    return response.data
  },

  // Update environment variable
  updateEnvVar: async (id: string, data: {
    value?: string
    type?: string
    tags?: string[]
    description?: string
    updated_by: string
  }) => {
    const response = await apiClient.put(`/envvars/${id}`, data)
    return response.data
  },

  // Delete environment variable
  deleteEnvVar: async (id: string, deleted_by: string) => {
    const response = await apiClient.delete(`/envvars/${id}`, {
      data: deleted_by
    })
    return response.data
  },

  // Get environment variable versions
  getEnvVarVersions: async (id: string) => {
    const response = await apiClient.get(`/envvars/${id}/versions`)
    return response.data
  },

  // Rollback environment variable
  rollbackEnvVar: async (id: string, version: number, rolled_back_by: string) => {
    const response = await apiClient.post(`/envvars/${id}/rollback`, {
      version,
      rolled_back_by
    })
    return response.data
  },

  // Reveal secret
  revealSecret: async (id: string, justification: string, ttl_seconds: number, requested_by: string) => {
    const response = await apiClient.post(`/envvars/${id}/reveal`, {
      justification,
      ttl_seconds,
      requested_by
    })
    return response.data
  },

  // Diff environments
  diffEnvironments: async (env1: string, env2: string) => {
    const response = await apiClient.get(`/envvars/diff/${env1}/${env2}`)
    return response.data
  },

  // Export to Kubernetes Secret
  exportToK8sSecret: async (data: {
    service_id: string
    environment?: string
    scope_level?: string
    scope_ref_id?: string
    exported_by: string
  }) => {
    const response = await apiClient.post('/envvars/export/k8s-secret', data)
    return response.data
  },

  // Export to Kubernetes ConfigMap
  exportToK8sConfigMap: async (data: {
    service_id: string
    environment?: string
    scope_level?: string
    scope_ref_id?: string
    exported_by: string
  }) => {
    const response = await apiClient.post('/envvars/export/k8s-configmap', data)
    return response.data
  },

  // Export to .env
  exportToDotEnv: async (data: {
    service_id?: string
    environment?: string
    scope_level?: string
    scope_ref_id?: string
    exported_by: string
  }) => {
    const response = await apiClient.post('/envvars/export/dotenv', data)
    return response.data
  }
}

// Releases API
export const releaseApi = {
  // List releases
  listReleases: async (params: {
    service_id?: string
    environment?: string
    status?: string
    page?: number
    size?: number
  }) => {
    const response = await apiClient.get('/releases', { params })
    return response.data
  },

  // Get release by ID
  getRelease: async (id: string) => {
    const response = await apiClient.get(`/releases/${id}`)
    return response.data
  },

  // Create release
  createRelease: async (data: {
    service_id: string
    environment: string
    title: string
    description?: string
    changes: unknown[]
    created_by: string
  }) => {
    const response = await apiClient.post('/releases', data)
    return response.data
  },

  // Approve release
  approveRelease: async (id: string, approver_id: string, comment?: string) => {
    const response = await apiClient.post(`/releases/${id}/approve`, {
      approver_id,
      comment
    })
    return response.data
  },

  // Apply release
  applyRelease: async (id: string, applied_by: string) => {
    const response = await apiClient.post(`/releases/${id}/apply`, {
      applied_by
    })
    return response.data
  },

  // Get release approvals
  getReleaseApprovals: async (id: string) => {
    const response = await apiClient.get(`/releases/${id}/approvals`)
    return response.data
  },

  // Get release status
  getReleaseStatus: async (id: string) => {
    const response = await apiClient.get(`/releases/${id}/status`)
    return response.data
  }
}

// Audit API
export const auditApi = {
  // Get audit events
  getAuditEvents: async (params: {
    actor?: string
    action?: string
    target_type?: string
    target_id?: string
    page?: number
    size?: number
  }) => {
    const response = await apiClient.get('/audit/events', { params })
    return response.data
  }
}

// Auth API
export const authApi = {
  // Login
  login: async (username: string, password: string) => {
    const response = await apiClient.post('/auth/login', {
      username,
      password
    })
    return response.data
  },

  // Register
  register: async (username: string, password: string, email: string) => {
    const response = await apiClient.post('/auth/register', {
      username,
      password,
      email
    })
    return response.data
  },

  // Logout
  logout: async () => {
    const response = await apiClient.post('/auth/logout')
    return response.data
  },

  // Get current user
  getCurrentUser: async () => {
    const response = await apiClient.get('/auth/me')
    return response.data
  }
}

export default apiClient
