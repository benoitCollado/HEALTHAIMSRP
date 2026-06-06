import { describe, expect, it } from 'vitest'
import { AIRFLOW_UI_URL, API_BASE_URL } from './config'

describe('config', () => {
  it('utilise le préfixe API du proxy nginx par défaut', () => {
    expect(API_BASE_URL).toBe('/api')
  })

  it('fournit une URL Airflow par défaut', () => {
    expect(AIRFLOW_UI_URL).toBe('http://localhost:8080')
  })
})
