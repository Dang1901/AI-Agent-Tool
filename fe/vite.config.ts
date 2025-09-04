// vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { fileURLToPath } from 'node:url'
import { dirname, resolve } from 'node:path'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@app': resolve(__dirname, 'src/app'),
      '@api': resolve(__dirname, 'src/api'),
      '@assets': resolve(__dirname, 'src/assets'),
      '@components': resolve(__dirname, 'src/components'),
      '@features': resolve(__dirname, 'src/features'),
      '@hooks': resolve(__dirname, 'src/hooks'),
      '@pages': resolve(__dirname, 'src/pages'),
      '@router': resolve(__dirname, 'src/router'),
      '@store': resolve(__dirname, 'src/store'),
      '@types': resolve(__dirname, 'src/types'),
      '@applications': resolve(__dirname, 'src/applications'),
    },
  },
})
