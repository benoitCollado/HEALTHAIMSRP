import { describe, expect, it } from 'vitest'
import { AIRFLOW_UI_URL, API_BASE_URL } from './config'

describe('config', () => {
  it('utilise une URL API vide par défaut (proxy nginx)', () => {
    expect(API_BASE_URL).toBe('')
  })

  it('fournit une URL Airflow par défaut', () => {
    expect(AIRFLOW_UI_URL).toBe('http://localhost:8080')
  })
})
