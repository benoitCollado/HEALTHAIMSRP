import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/__tests__/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'lcov'],
      include: ['src/services/**', 'src/router.ts']
    }
  },
  base: '/',
  server: {
    port: 5173,
    host: '0.0.0.0',
    strictPort: true,
    proxy: {
      '^/(login|utilisateurs|metriques-sante|activites|consommations|objectifs|aliments|exercices)(/.*)?$': {
        target: 'http://localhost:8089',
        changeOrigin: true
      }
    }
  }
})
