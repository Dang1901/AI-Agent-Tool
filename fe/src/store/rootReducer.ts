// src/store/rootReducer.ts
import { combineReducers } from '@reduxjs/toolkit'
import authReducer from './slice'

const rootReducer = combineReducers({
  auth: authReducer,
})

export default rootReducer
export type RootState = ReturnType<typeof rootReducer>
