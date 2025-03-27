import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/upload': 'http://localhost:8000',
      '/download': 'http://localhost:8000'
    }
  }
})
