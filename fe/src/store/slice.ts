import { createSlice, type PayloadAction } from '@reduxjs/toolkit'
import type { AuthState, UserProfile } from 'src/infrastructure/auth.types'


const initialState: AuthState = {
  isAuthenticated: false,
  user: null,
}

const slice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setSession(state, action: PayloadAction<{ user: UserProfile }>) {
      state.isAuthenticated = true
      state.user = action.payload.user
    },
    clearSession(state) {
      state.isAuthenticated = false
      state.user = null
    },
  },
})

export const { setSession, clearSession } = slice.actions
export default slice.reducer
