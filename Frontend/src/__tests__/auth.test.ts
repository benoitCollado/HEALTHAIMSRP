import { describe, it, expect, beforeEach, vi } from 'vitest'
import { auth } from '../services/auth'

// ──────────────────────────────────────────────
// Helpers
// ──────────────────────────────────────────────

/** Build a minimal JWT (header.payload.signature) where payload is base64url-encoded JSON */
function buildJwt(payload: Record<string, unknown>): string {
  const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }))
    .replace(/=/g, '').replace(/\+/g, '-').replace(/\//g, '_')
  const body = btoa(JSON.stringify(payload))
    .replace(/=/g, '').replace(/\+/g, '-').replace(/\//g, '_')
  return `${header}.${body}.signature`
}

function futureExp() {
  return Math.floor(Date.now() / 1000) + 3600 // +1h
}

function pastExp() {
  return Math.floor(Date.now() / 1000) - 3600 // -1h
}

// ──────────────────────────────────────────────
// Tests
// ──────────────────────────────────────────────

describe('auth service', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.restoreAllMocks()
  })

  // ── getCurrentUser ──────────────────────────
  describe('getCurrentUser', () => {
    it('returns null when localStorage is empty', () => {
      expect(auth.getCurrentUser()).toBeNull()
    })

    it('returns the stored user', () => {
      const user = { id: '1', username: 'alice', role: 'user' as const }
      localStorage.setItem('app_user', JSON.stringify(user))
      expect(auth.getCurrentUser()).toEqual(user)
    })

    it('returns null when stored value is malformed JSON', () => {
      localStorage.setItem('app_user', '{bad json')
      expect(auth.getCurrentUser()).toBeNull()
    })
  })

  // ── getToken ────────────────────────────────
  describe('getToken', () => {
    it('returns null when no token stored', () => {
      expect(auth.getToken()).toBeNull()
    })

    it('returns the stored token string', () => {
      localStorage.setItem('app_token', 'mytoken')
      expect(auth.getToken()).toBe('mytoken')
    })
  })

  // ── logout ──────────────────────────────────
  describe('logout', () => {
    it('clears user and token from localStorage', () => {
      localStorage.setItem('app_user', JSON.stringify({ id: '1', username: 'alice', role: 'user' }))
      localStorage.setItem('app_token', 'tok')
      auth.logout()
      expect(localStorage.getItem('app_user')).toBeNull()
      expect(localStorage.getItem('app_token')).toBeNull()
    })
  })

  // ── hasRole ─────────────────────────────────
  describe('hasRole', () => {
    it('returns false when no user is stored', () => {
      expect(auth.hasRole('admin')).toBe(false)
    })

    it('returns true when role matches', () => {
      localStorage.setItem('app_user', JSON.stringify({ id: '1', username: 'bob', role: 'admin' }))
      expect(auth.hasRole('admin')).toBe(true)
    })

    it('returns false when role does not match', () => {
      localStorage.setItem('app_user', JSON.stringify({ id: '2', username: 'carol', role: 'user' }))
      expect(auth.hasRole('admin')).toBe(false)
    })
  })

  // ── isAdmin ─────────────────────────────────
  describe('isAdmin', () => {
    it('returns false when user has role "user"', () => {
      localStorage.setItem('app_user', JSON.stringify({ id: '3', username: 'dave', role: 'user' }))
      expect(auth.isAdmin()).toBe(false)
    })

    it('returns true when user has role "admin"', () => {
      localStorage.setItem('app_user', JSON.stringify({ id: '4', username: 'eve', role: 'admin' }))
      expect(auth.isAdmin()).toBe(true)
    })
  })

  // ── isTokenExpired ──────────────────────────
  describe('isTokenExpired', () => {
    it('returns true when no token is present', () => {
      expect(auth.isTokenExpired()).toBe(true)
    })

    it('returns true when token is malformed', () => {
      localStorage.setItem('app_token', 'not.a.jwt')
      // payload "not" does not have "exp"
      expect(auth.isTokenExpired()).toBe(true)
    })

    it('returns false when token exp is in the future', () => {
      const token = buildJwt({ sub: '1', exp: futureExp() })
      localStorage.setItem('app_token', token)
      expect(auth.isTokenExpired()).toBe(false)
    })

    it('returns true when token exp is in the past', () => {
      const token = buildJwt({ sub: '1', exp: pastExp() })
      localStorage.setItem('app_token', token)
      expect(auth.isTokenExpired()).toBe(true)
    })
  })

  // ── isAuthenticated ─────────────────────────
  describe('isAuthenticated', () => {
    it('returns false when no user and no token', () => {
      expect(auth.isAuthenticated()).toBe(false)
    })

    it('returns false when user is present but token is expired', () => {
      localStorage.setItem('app_user', JSON.stringify({ id: '1', username: 'alice', role: 'user' }))
      const token = buildJwt({ sub: '1', exp: pastExp() })
      localStorage.setItem('app_token', token)
      expect(auth.isAuthenticated()).toBe(false)
    })

    it('returns true when user is present and token is valid', () => {
      localStorage.setItem('app_user', JSON.stringify({ id: '1', username: 'alice', role: 'user' }))
      const token = buildJwt({ sub: '1', exp: futureExp() })
      localStorage.setItem('app_token', token)
      expect(auth.isAuthenticated()).toBe(true)
    })
  })

  // ── login ───────────────────────────────────
  describe('login', () => {
    it('returns success and stores user+token on valid credentials', async () => {
      const token = buildJwt({ sub: 42, is_admin: false, exp: futureExp() })
      vi.mocked(fetch).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ access_token: token, token_type: 'bearer' })
      } as Response)

      const result = await auth.login('alice', 'password')
      expect(result.success).toBe(true)
      expect(result.user?.username).toBe('alice')
      expect(result.user?.role).toBe('user')
      expect(localStorage.getItem('app_token')).toBe(token)
    })

    it('sets role to "admin" when is_admin is true in JWT', async () => {
      const token = buildJwt({ sub: 1, is_admin: true, exp: futureExp() })
      vi.mocked(fetch).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ access_token: token, token_type: 'bearer' })
      } as Response)

      const result = await auth.login('admin', 'secret')
      expect(result.user?.role).toBe('admin')
    })

    it('returns failure when HTTP response is not ok', async () => {
      vi.mocked(fetch).mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ detail: 'Identifiants incorrects' })
      } as Response)

      const result = await auth.login('bad', 'creds')
      expect(result.success).toBe(false)
      expect(result.error).toBe('Identifiants incorrects')
    })

    it('returns failure when fetch throws a network error', async () => {
      vi.mocked(fetch).mockRejectedValueOnce(new Error('Network failure'))

      const result = await auth.login('alice', 'pw')
      expect(result.success).toBe(false)
      expect(result.error).toBe('Network failure')
    })

    it('returns failure when JWT has no sub', async () => {
      const token = buildJwt({ exp: futureExp() }) // no sub
      vi.mocked(fetch).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ access_token: token, token_type: 'bearer' })
      } as Response)

      const result = await auth.login('alice', 'pw')
      expect(result.success).toBe(false)
    })
  })
})
