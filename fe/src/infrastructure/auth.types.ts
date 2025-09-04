export interface UserProfile {
  id: number
  email: string
  name?: string
  roles?: string[]
}

export interface AuthState {
  isAuthenticated: boolean
  user: UserProfile | null
}
