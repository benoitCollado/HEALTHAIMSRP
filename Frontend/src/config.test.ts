import { describe, expect, it } from 'vitest'
import { AIRFLOW_UI_URL, API_BASE_URL } from './config'

describe('config', () => {
  it('lit VITE_API_URL depuis .env.example à la racine du repo', () => {
    expect(API_BASE_URL).toBe('https://healthai.mondomaine.com/api')
  })

  it('fournit une URL Airflow par défaut', () => {
    expect(AIRFLOW_UI_URL).toBe('http://localhost:8080')
  })
})
