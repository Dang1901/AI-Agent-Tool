// src/store/store.ts
import { configureStore } from '@reduxjs/toolkit'
import { persistReducer, persistStore } from 'redux-persist'
import storage from 'redux-persist/lib/storage'
import type { RootState } from './rootReducer'
import rootReducer from './rootReducer'

// (Tuỳ chọn) mã hoá khi phải persist token — KHÔNG khuyến nghị nếu có cookie httpOnly
// import createEncryptor from 'redux-persist-transform-encrypt'
// const encryptor = createEncryptor({ secretKey: import.meta.env.VITE_PERSIST_SECRET || 'dev-secret' })

const persistConfig = {
  key: 'APP_STATE_V1',
  storage,
  whitelist: ['auth'], // chỉ lưu auth slice (đã tối giản)
  // transforms: [encryptor], // bật nếu bạn bắt buộc lưu token
}

const persistedReducer = persistReducer<RootState>(persistConfig, rootReducer)

export const store = configureStore({
  reducer: persistedReducer,
  devTools: import.meta.env.DEV,
  middleware: (getDefault) =>
    getDefault({
      serializableCheck: false, // đơn giản hoá cho persist
    }),
})

export const persistor = persistStore(store)

export type AppDispatch = typeof store.dispatch
