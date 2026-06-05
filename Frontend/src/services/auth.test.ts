import { afterEach, describe, expect, it, vi } from 'vitest'
import { auth } from './auth'
import { buildTestJwt } from '../test-utils/jwt'

function mockLoginResponse(token: string, status = 200) {
  vi.stubGlobal(
    'fetch',
    vi.fn().mockResolvedValue({
      ok: status >= 200 && status < 300,
      status,
      json: async () => ({ access_token: token, token_type: 'bearer' })
    })
  )
}

describe('auth service', () => {
  afterEach(() => {
    auth.logout()
  })

  it('retourne null si aucun utilisateur en session', () => {
    expect(auth.getCurrentUser()).toBeNull()
    expect(auth.isAuthenticated()).toBe(false)
  })

  it('connecte un administrateur et persiste la session', async () => {
    const token = buildTestJwt({
      sub: 42,
      is_admin: true,
      exp: Math.floor(Date.now() / 1000) + 3600
    })
    mockLoginResponse(token)

    const result = await auth.login('admin', 'secret')

    expect(result.success).toBe(true)
    expect(result.user).toEqual({
      id: '42',
      username: 'admin',
      role: 'admin'
    })
    expect(auth.getCurrentUser()?.role).toBe('admin')
    expect(auth.isAdmin()).toBe(true)
    expect(auth.isAuthenticated()).toBe(true)
    expect(auth.getToken()).toBe(token)
  })

  it('connecte un utilisateur standard', async () => {
    const token = buildTestJwt({
      sub: 'user-1',
      is_admin: false,
      exp: Math.floor(Date.now() / 1000) + 3600
    })
    mockLoginResponse(token)

    const result = await auth.login('alice', 'secret')

    expect(result.success).toBe(true)
    expect(result.user?.role).toBe('user')
    expect(auth.isAdmin()).toBe(false)
    expect(auth.hasRole('user')).toBe(true)
  })

  it('retourne une erreur si le backend refuse la connexion', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: false,
        status: 401,
        json: async () => ({ detail: 'Identifiants invalides' })
      })
    )

    const result = await auth.login('wrong', 'wrong')

    expect(result.success).toBe(false)
    expect(result.error).toBe('Identifiants invalides')
    expect(auth.getCurrentUser()).toBeNull()
  })

  it('détecte un token expiré', async () => {
    const token = buildTestJwt({
      sub: 1,
      is_admin: false,
      exp: Math.floor(Date.now() / 1000) - 60
    })
    mockLoginResponse(token)

    await auth.login('expired', 'secret')

    expect(auth.isTokenExpired()).toBe(true)
    expect(auth.isAuthenticated()).toBe(false)
  })

  it('efface la session au logout', async () => {
    const token = buildTestJwt({
      sub: 1,
      is_admin: true,
      exp: Math.floor(Date.now() / 1000) + 3600
    })
    mockLoginResponse(token)
    await auth.login('admin', 'secret')

    auth.logout()

    expect(auth.getCurrentUser()).toBeNull()
    expect(auth.getToken()).toBeNull()
  })
})
