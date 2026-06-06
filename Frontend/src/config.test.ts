import { describe, expect, it } from 'vitest'
import { AIRFLOW_UI_URL, API_BASE_URL } from './config'

describe('config', () => {
  it('utilise le prefixe API du proxy nginx par defaut', () => {
    const expectedApiBase = (import.meta.env.VITE_API_URL || '/api').replace(/\/$/, '') || '/api'
    expect(API_BASE_URL).toBe(expectedApiBase)
  })

  it('fournit une URL Airflow par defaut', () => {
    expect(AIRFLOW_UI_URL).toBe('http://localhost:8080')
  })
})
