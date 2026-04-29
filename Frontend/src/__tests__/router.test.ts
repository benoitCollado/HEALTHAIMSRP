import { describe, it, expect, beforeEach, vi } from 'vitest'
import { createRouter, createMemoryHistory } from 'vue-router'
import { defineComponent } from 'vue'

// ── Mock auth before importing router ────────────────────────────────────────
const mockAuth = {
  isAuthenticated: vi.fn(() => false),
  isAdmin: vi.fn(() => false)
}

vi.mock('../services/auth', () => ({ auth: mockAuth }))

// ── Stub components (router lazy-loads pages, we only test guards) ───────────
const Stub = defineComponent({ template: '<div />' })

// Re-create the router from scratch so we can control auth state per test
function buildRouter() {
  const routes = [
    { path: '/connexion', name: 'Connexion', component: Stub, meta: { requiresAuth: false } },
    { path: '/page-accueil', name: 'PageAccueil', component: Stub, meta: { requiresAuth: true } },
    {
      path: '/dashboard',
      name: 'Dashboard',
      component: Stub,
      meta: { requiresAuth: true, requiresAdmin: true }
    },
    { path: '/:pathMatch(.*)*', redirect: '/connexion' }
  ]

  const router = createRouter({ history: createMemoryHistory(), routes })

  router.beforeEach((to, _from, next) => {
    const requiresAuth = to.meta.requiresAuth !== false
    const requiresAdmin = to.meta.requiresAdmin === true
    const isAuthenticated = mockAuth.isAuthenticated()
    const isAdmin = mockAuth.isAdmin()

    if (to.path === '/connexion') {
      return isAuthenticated ? next('/page-accueil') : next()
    }
    if (requiresAuth && !isAuthenticated) return next('/connexion')
    if (requiresAdmin && !isAdmin) return next('/page-accueil')
    next()
  })

  return router
}

// ─────────────────────────────────────────────────────────────────────────────

describe('router navigation guards', () => {
  let router: ReturnType<typeof buildRouter>

  beforeEach(() => {
    mockAuth.isAuthenticated.mockReturnValue(false)
    mockAuth.isAdmin.mockReturnValue(false)
    router = buildRouter()
  })

  it('redirects unauthenticated user from /page-accueil to /connexion', async () => {
    await router.push('/page-accueil')
    expect(router.currentRoute.value.path).toBe('/connexion')
  })

  it('redirects unauthenticated user from /dashboard to /connexion', async () => {
    await router.push('/dashboard')
    expect(router.currentRoute.value.path).toBe('/connexion')
  })

  it('allows unauthenticated user to access /connexion', async () => {
    await router.push('/connexion')
    expect(router.currentRoute.value.path).toBe('/connexion')
  })

  it('redirects authenticated user from /connexion to /page-accueil', async () => {
    mockAuth.isAuthenticated.mockReturnValue(true)
    await router.push('/connexion')
    expect(router.currentRoute.value.path).toBe('/page-accueil')
  })

  it('allows authenticated non-admin to access /page-accueil', async () => {
    mockAuth.isAuthenticated.mockReturnValue(true)
    await router.push('/page-accueil')
    expect(router.currentRoute.value.path).toBe('/page-accueil')
  })

  it('redirects authenticated non-admin from /dashboard to /page-accueil', async () => {
    mockAuth.isAuthenticated.mockReturnValue(true)
    mockAuth.isAdmin.mockReturnValue(false)
    await router.push('/dashboard')
    expect(router.currentRoute.value.path).toBe('/page-accueil')
  })

  it('allows admin to access /dashboard', async () => {
    mockAuth.isAuthenticated.mockReturnValue(true)
    mockAuth.isAdmin.mockReturnValue(true)
    await router.push('/dashboard')
    expect(router.currentRoute.value.path).toBe('/dashboard')
  })

  it('redirects unknown path to /connexion', async () => {
    await router.push('/nonexistent-route')
    expect(router.currentRoute.value.path).toBe('/connexion')
  })
})
