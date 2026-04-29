import { describe, it, expect, beforeEach, vi } from 'vitest'

// ── Mock auth so getToken() is controllable ──────────────────────────────────
vi.mock('../services/auth', () => ({
  auth: {
    getToken: vi.fn(() => 'test-token')
  }
}))

import {
  getDashboard,
  getFlux,
  searchUtilisateurs,
  getUtilisateurDonnees,
  getAnomalies,
  validerAnomalie,
  getFluxCsvList,
  validateFluxCsv,
  rejectFluxCsv
} from '../services/adminApi'

// ── Helpers ──────────────────────────────────────────────────────────────────

function okJson(data: unknown): Response {
  return {
    ok: true,
    status: 200,
    json: async () => data
  } as Response
}

function notOk(status = 500): Response {
  return { ok: false, status, json: async () => ({}) } as Response
}

// ── Tests ────────────────────────────────────────────────────────────────────

describe('adminApi', () => {
  beforeEach(() => {
    vi.mocked(fetch).mockReset()
  })

  // ── getDashboard ────────────────────────────────────────────────────────────
  describe('getDashboard', () => {
    it('calls /admin/dashboard with Authorization header and returns data', async () => {
      const mockData = { qualite_donnees: { score_pct: 95 } }
      vi.mocked(fetch).mockResolvedValueOnce(okJson(mockData))

      const result = await getDashboard()
      expect(result).toEqual(mockData)
      const [url, options] = vi.mocked(fetch).mock.calls[0] as [string, RequestInit]
      expect(url).toContain('/admin/dashboard')
      expect((options?.headers as Record<string, string>)['Authorization']).toBe('Bearer test-token')
    })

    it('throws when response is not ok', async () => {
      vi.mocked(fetch).mockResolvedValueOnce(notOk(500))
      await expect(getDashboard()).rejects.toThrow('Erreur 500')
    })
  })

  // ── getFlux ─────────────────────────────────────────────────────────────────
  describe('getFlux', () => {
    it('returns parsed flux data', async () => {
      const mockFlux = { valides: [], encours: [], refuses: [], flux_metadonnees: {} }
      vi.mocked(fetch).mockResolvedValueOnce(okJson(mockFlux))
      const result = await getFlux()
      expect(result).toEqual(mockFlux)
    })

    it('throws on 401', async () => {
      vi.mocked(fetch).mockResolvedValueOnce(notOk(401))
      await expect(getFlux()).rejects.toThrow('Erreur 401')
    })
  })

  // ── searchUtilisateurs ──────────────────────────────────────────────────────
  describe('searchUtilisateurs', () => {
    it('calls /admin/utilisateurs without query param when no argument', async () => {
      vi.mocked(fetch).mockResolvedValueOnce(okJson({ utilisateurs: [], total: 0 }))
      await searchUtilisateurs()
      const [url] = vi.mocked(fetch).mock.calls[0] as [string, RequestInit]
      expect(url).toContain('/admin/utilisateurs')
      expect(url).not.toContain('?q=')
    })

    it('appends q= param when search string is provided', async () => {
      vi.mocked(fetch).mockResolvedValueOnce(okJson({ utilisateurs: [], total: 0 }))
      await searchUtilisateurs('alice')
      const [url] = vi.mocked(fetch).mock.calls[0] as [string, RequestInit]
      expect(url).toContain('?q=alice')
    })

    it('URL-encodes the search query', async () => {
      vi.mocked(fetch).mockResolvedValueOnce(okJson({ utilisateurs: [], total: 0 }))
      await searchUtilisateurs('jean pierre')
      const [url] = vi.mocked(fetch).mock.calls[0] as [string, RequestInit]
      expect(url).toContain('jean%20pierre')
    })

    it('throws on error', async () => {
      vi.mocked(fetch).mockResolvedValueOnce(notOk(403))
      await expect(searchUtilisateurs()).rejects.toThrow('Erreur 403')
    })
  })

  // ── getUtilisateurDonnees ───────────────────────────────────────────────────
  describe('getUtilisateurDonnees', () => {
    it('calls /admin/utilisateurs/:id and returns data', async () => {
      const mockUser = { utilisateur: { id_utilisateur: 7 }, consommations: [], activites: [], metriques: [], objectifs: [] }
      vi.mocked(fetch).mockResolvedValueOnce(okJson(mockUser))
      const result = await getUtilisateurDonnees(7)
      expect(result).toEqual(mockUser)
      const [url] = vi.mocked(fetch).mock.calls[0] as [string, RequestInit]
      expect(url).toContain('/admin/utilisateurs/7')
    })

    it('throws when user is not found', async () => {
      vi.mocked(fetch).mockResolvedValueOnce(notOk(404))
      await expect(getUtilisateurDonnees(99)).rejects.toThrow('Erreur 404')
    })
  })

  // ── getAnomalies ────────────────────────────────────────────────────────────
  describe('getAnomalies', () => {
    it('calls /admin/anomalies without type filter by default', async () => {
      vi.mocked(fetch).mockResolvedValueOnce(okJson({ anomalies: [], total: 0 }))
      await getAnomalies()
      const [url] = vi.mocked(fetch).mock.calls[0] as [string, RequestInit]
      expect(url).not.toContain('type_anomalie')
    })

    it('appends type_anomalie param when type is specified', async () => {
      vi.mocked(fetch).mockResolvedValueOnce(okJson({ anomalies: [], total: 0 }))
      await getAnomalies('poids')
      const [url] = vi.mocked(fetch).mock.calls[0] as [string, RequestInit]
      expect(url).toContain('type_anomalie=poids')
    })
  })

  // ── validerAnomalie ─────────────────────────────────────────────────────────
  describe('validerAnomalie', () => {
    it('sends POST to /admin/anomalies/:id/valider', async () => {
      vi.mocked(fetch).mockResolvedValueOnce(okJson({ success: true, message: 'OK' }))
      const result = await validerAnomalie('anom-123')
      expect(result.success).toBe(true)
      const [url, options] = vi.mocked(fetch).mock.calls[0] as [string, RequestInit]
      expect(url).toContain('/admin/anomalies/anom-123/valider')
      expect(options?.method).toBe('POST')
    })
  })

  // ── getFluxCsvList ──────────────────────────────────────────────────────────
  describe('getFluxCsvList', () => {
    it('fetches csv list without params by default', async () => {
      vi.mocked(fetch).mockResolvedValueOnce(okJson({ import: [], export: [] }))
      await getFluxCsvList()
      const [url] = vi.mocked(fetch).mock.calls[0] as [string, RequestInit]
      expect(url).toContain('/admin/flux/csv')
      expect(url).not.toContain('?')
    })

    it('appends type and status query params when provided', async () => {
      vi.mocked(fetch).mockResolvedValueOnce(okJson({ import: [], export: [] }))
      await getFluxCsvList('activites', 'pending')
      const [url] = vi.mocked(fetch).mock.calls[0] as [string, RequestInit]
      expect(url).toContain('type_csv=activites')
      expect(url).toContain('status=pending')
    })
  })

  // ── validateFluxCsv / rejectFluxCsv ────────────────────────────────────────
  describe('validateFluxCsv', () => {
    it('sends POST to /admin/flux/csv/:filename/validate', async () => {
      vi.mocked(fetch).mockResolvedValueOnce(okJson({ success: true, message: 'validated' }))
      const result = await validateFluxCsv('file.csv')
      expect(result.success).toBe(true)
      const [url, options] = vi.mocked(fetch).mock.calls[0] as [string, RequestInit]
      expect(url).toContain('/validate')
      expect(options?.method).toBe('POST')
    })
  })

  describe('rejectFluxCsv', () => {
    it('sends POST to /admin/flux/csv/:filename/reject', async () => {
      vi.mocked(fetch).mockResolvedValueOnce(okJson({ success: true, message: 'rejected' }))
      const result = await rejectFluxCsv('file.csv')
      expect(result.success).toBe(true)
      const [url, options] = vi.mocked(fetch).mock.calls[0] as [string, RequestInit]
      expect(url).toContain('/reject')
      expect(options?.method).toBe('POST')
    })
  })
})
