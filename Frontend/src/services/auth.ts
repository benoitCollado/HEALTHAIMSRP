export type UserRole = 'admin' | 'user' | null

export interface User {
  id: string
  username: string
  role: UserRole
}

import { API_BASE_URL } from '../config'

const STORAGE_KEY = 'app_user'
const TOKEN_KEY = 'app_token'

interface LoginResult {
  success: boolean
  user?: User
  error?: string
}

interface JwtPayload {
  sub?: string | number
  is_admin?: boolean
}

function decodeJwtPayload(token: string): JwtPayload | null {
  const parts = token.split('.')
  if (parts.length < 2) return null

  try {
    const base64 = parts[1].replace(/-/g, '+').replace(/_/g, '/')
    const json = decodeURIComponent(
      atob(base64)
        .split('')
        .map((char) => `%${(`00${char.charCodeAt(0).toString(16)}`).slice(-2)}`)
        .join('')
    )

    return JSON.parse(json)
  } catch {
    return null
  }
}

async function loginRequest(username: string, password: string): Promise<{ access_token: string; token_type: string }> {
  const body = new URLSearchParams({ username, password }).toString()
  const response = await fetch(`${API_BASE_URL}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body
  })

  if (!response.ok) {
    let errorMessage = 'Erreur de connexion'
    try {
      const errorData = await response.json()
      errorMessage = errorData?.detail || errorMessage
    } catch {
      // no-op
    }
    throw new Error(errorMessage)
  }

  return response.json()
}

export const auth = {
  // Get current user from localStorage
  getCurrentUser(): User | null {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (!stored) return null
    try {
      return JSON.parse(stored)
    } catch {
      return null
    }
  },

  // Login with username/password using FastAPI backend
  async login(username: string, password: string): Promise<LoginResult> {
    try {
      const result = await loginRequest(username, password)
      const payload = decodeJwtPayload(result.access_token)

      if (!payload?.sub) {
        return { success: false, error: 'Token invalide' }
      }

      const role: UserRole = payload.is_admin ? 'admin' : 'user'
      const sessionUser: User = {
        id: String(payload.sub),
        username,
        role
      }

      localStorage.setItem(STORAGE_KEY, JSON.stringify(sessionUser))
      localStorage.setItem(TOKEN_KEY, result.access_token)

      return { success: true, user: sessionUser }
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Erreur de connexion'
      return { success: false, error: message }
    }
  },

  // Logout
  logout(): void {
    localStorage.removeItem(STORAGE_KEY)
    localStorage.removeItem(TOKEN_KEY)
  },

  // Get access token
  getToken(): string | null {
    return localStorage.getItem(TOKEN_KEY)
  },

  // Check if user has a specific role
  hasRole(role: UserRole): boolean {
    const user = this.getCurrentUser()
    return user?.role === role
  },

  // Check if user is authenticated
  isAuthenticated(): boolean {
    return this.getCurrentUser() !== null
  },

  // Check if user is admin
  isAdmin(): boolean {
    return this.hasRole('admin')
  }
}
