import { existsSync, readFileSync } from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { loadEnv } from 'vite'
import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')

function parseEnvFile(filePath: string): Record<string, string> {
  if (!existsSync(filePath)) return {}

  const vars: Record<string, string> = {}
  for (const line of readFileSync(filePath, 'utf8').split('\n')) {
    const trimmed = line.trim()
    if (!trimmed || trimmed.startsWith('#')) continue

    const eq = trimmed.indexOf('=')
    if (eq === -1) continue

    const key = trimmed.slice(0, eq).trim()
    let value = trimmed.slice(eq + 1).trim()
    if (
      (value.startsWith('"') && value.endsWith('"')) ||
      (value.startsWith("'") && value.endsWith("'"))
    ) {
      value = value.slice(1, -1)
    }
    vars[key] = value
  }
  return vars
}

function resolveViteEnv(mode: string) {
  const fromMode = loadEnv(mode, repoRoot, 'VITE_')
  const fromDotEnv = parseEnvFile(path.join(repoRoot, '.env'))
  const fromExample = parseEnvFile(path.join(repoRoot, '.env.example'))

  const pick = (key: string, fallback = '') =>
    process.env[key] || fromMode[key] || fromDotEnv[key] || fromExample[key] || fallback

  // In local dev we must target the Vite proxy to avoid external placeholder URLs.
  const rawApiUrl = mode === 'development' ? '/api' : pick('VITE_API_URL')

  return {
    VITE_API_URL: rawApiUrl.replace(/\/$/, ''),
    VITE_AIRFLOW_UI_URL: pick('VITE_AIRFLOW_UI_URL', 'http://localhost:8080'),
  }
}

export default defineConfig(({ mode }) => {
  const viteEnv = resolveViteEnv(mode)

  return {
    plugins: [vue()],
    base: '/',
    envDir: repoRoot,
    define: {
      'import.meta.env.VITE_API_URL': JSON.stringify(viteEnv.VITE_API_URL),
      'import.meta.env.VITE_AIRFLOW_UI_URL': JSON.stringify(viteEnv.VITE_AIRFLOW_UI_URL),
    },
    server: {
      port: 5173,
      host: '0.0.0.0',
      strictPort: true,
      proxy: {
        '/api': {
          target: 'http://localhost:8000',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, ''),
        },
      },
    },
    test: {
      environment: 'jsdom',
      setupFiles: ['./vitest.setup.ts'],
      include: ['src/**/*.{test,spec}.{ts,tsx}'],
      coverage: {
        provider: 'v8',
        reporter: ['lcov'],
        reportsDirectory: './coverage',
        include: ['src/**/*.{ts,vue}'],
        exclude: ['src/**/*.test.ts', 'src/test-utils/**', 'src/data/**'],
      },
    },
  }
})
