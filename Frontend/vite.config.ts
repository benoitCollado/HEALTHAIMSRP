import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    host: '0.0.0.0',
    proxy: {
      '^/(login|utilisateurs|metriques-sante|activites|consommations|objectifs|aliments|exercices)(/.*)?$': {
        target: 'http://localhost:8089',
        changeOrigin: true
      }
    }
  }
})
