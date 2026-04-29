import { describe, it, expect, beforeEach, vi } from 'vitest'
import {
  getDashboardStats,
  getActivityData,
  getValidationRateData,
  getFluxData,
  validerFlux,
  refuserFlux
} from '../services/api'

describe('api service (mock data)', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  describe('getDashboardStats', () => {
    it('resolves with dashboard stats object', async () => {
      const promise = getDashboardStats()
      vi.runAllTimers()
      const result = await promise
      expect(result).toBeDefined()
      expect(typeof result).toBe('object')
    })
  })

  describe('getActivityData', () => {
    it('resolves with activity data', async () => {
      const promise = getActivityData()
      vi.runAllTimers()
      const result = await promise
      expect(result).toBeDefined()
    })
  })

  describe('getValidationRateData', () => {
    it('resolves with validation rate data', async () => {
      const promise = getValidationRateData()
      vi.runAllTimers()
      const result = await promise
      expect(result).toBeDefined()
    })
  })

  describe('getFluxData', () => {
    it('resolves with flux data', async () => {
      const promise = getFluxData()
      vi.runAllTimers()
      const result = await promise
      expect(result).toBeDefined()
    })
  })

  describe('validerFlux', () => {
    it('resolves with success true and the given flux id', async () => {
      const promise = validerFlux('flux-42')
      vi.runAllTimers()
      const result = await promise as { success: boolean; fluxId: string }
      expect(result.success).toBe(true)
      expect(result.fluxId).toBe('flux-42')
    })
  })

  describe('refuserFlux', () => {
    it('resolves with success true and the given flux id', async () => {
      const promise = refuserFlux('flux-99')
      vi.runAllTimers()
      const result = await promise as { success: boolean; fluxId: string }
      expect(result.success).toBe(true)
      expect(result.fluxId).toBe('flux-99')
    })
  })
})
