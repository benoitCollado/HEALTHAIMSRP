// Mock authentication service
// In production, replace with real API calls to FastAPI backend

export type UserRole = 'admin' | 'user' | null

export interface User {
  id: string
  username: string
  role: UserRole
}

const STORAGE_KEY = 'app_user'

// Mock user database
const users = [
  { id: '1', username: 'admin', password: 'admin', role: 'admin' as UserRole },
  { id: '2', username: 'user', password: 'user', role: 'user' as UserRole }
]

export const auth = {
  // Get current user from sessionStorage
  getCurrentUser(): User | null {
    const stored = sessionStorage.getItem(STORAGE_KEY)
    if (!stored) return null
    try {
      return JSON.parse(stored)
    } catch {
      return null
    }
  },

  // Login with username/password
  login(username: string, password: string): { success: boolean; user?: User; error?: string } {
    const user = users.find(u => u.username === username)
    if (!user) {
      return { success: false, error: 'Utilisateur non trouvé' }
    }

    // In production: hash password and verify on backend
    if (user.password !== password) {
      return { success: false, error: 'Mot de passe incorrect' }
    }

    const sessionUser: User = {
      id: user.id,
      username: user.username,
      role: user.role
    }

    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(sessionUser))
    return { success: true, user: sessionUser }
  },

  // Logout
  logout(): void {
    sessionStorage.removeItem(STORAGE_KEY)
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
