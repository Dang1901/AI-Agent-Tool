// src/App.tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Provider } from 'react-redux'
import { RouterProvider } from 'react-router-dom'
import { PersistGate } from 'redux-persist/integration/react'
import { router } from './router'
import { persistor, store } from '@store/store'
import { Theme } from '@radix-ui/themes'
import { ToastProvider } from './contexts/ToastContext'
import '@radix-ui/themes/styles.css'


const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: 0, gcTime: 0 },
    mutations: { retry: 0 },
  },
})

export default function App() {
  return (
    <Provider store={store}>
      <QueryClientProvider client={queryClient}>
        <PersistGate loading={null} persistor={persistor}>
          <Theme
            appearance="dark"
            radius="large"
            scaling="100%"
            accentColor="indigo"
          >
            <ToastProvider>
              <RouterProvider router={router} />
            </ToastProvider>
          </Theme>
        </PersistGate>
      </QueryClientProvider>
    </Provider>
  )
}
