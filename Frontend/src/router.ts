import { createRouter, createWebHistory, NavigationGuardNext, RouteLocationNormalized } from 'vue-router'
import { auth } from './services/auth'

const routes = [
  { path: '/', redirect: '/connexion' },
  { path: '/connexion', name: 'Connexion', component: () => import('./pages/Connexion.vue'), meta: { requiresAuth: false } },
  { path: '/inscription', name: 'Inscription', component: () => import('./pages/Inscription.vue'), meta: { requiresAuth: false } },
  { path: '/page-accueil', name: 'PageAccueil', component: () => import('./pages/PageAccueil.vue'), meta: { requiresAuth: true } },
  { path: '/chat', name: 'ChatAssistant', component: () => import('./pages/ChatAssistant.vue'), meta: { requiresAuth: true } },
  { path: '/dashboard', name: 'Dashboard', component: () => import('./pages/Dashboard.vue'), meta: { requiresAuth: true, requiresAdmin: true } },
  { path: '/gestion-des-flux', name: 'GestionFlux', component: () => import('./pages/GestionFlux.vue'), meta: { requiresAuth: true, requiresAdmin: true } },
  { path: '/flux/:id', name: 'FluxDetail', component: () => import('./pages/FluxDetail.vue'), props: true, meta: { requiresAuth: true, requiresAdmin: true } },
  { path: '/nettoyage', name: 'Nettoyage', component: () => import('./pages/Nettoyage.vue'), meta: { requiresAuth: true, requiresAdmin: true } },
  { path: '/utilisateurs', name: 'Utilisateurs', component: () => import('./pages/Utilisateurs.vue'), meta: { requiresAuth: true, requiresAdmin: true } },
  { path: '/utilisateurs/:id', name: 'UtilisateurDetail', component: () => import('./pages/UtilisateurDetail.vue'), props: true, meta: { requiresAuth: true, requiresAdmin: true } },
  { path: '/test-backend', name: 'TestBackend', component: () => import('./pages/TestBackend.vue'), meta: { requiresAuth: true, requiresAdmin: true } },
  { path: '/page-view/:id?', name: 'PageView', component: () => import('./pages/PageView.vue'), meta: { requiresAuth: false } },
  { path: '/:pathMatch(.*)*', redirect: '/connexion' }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard to check authentication and authorization
router.beforeEach((to: RouteLocationNormalized, from: RouteLocationNormalized, next: NavigationGuardNext) => {
  const requiresAuth = to.meta.requiresAuth !== false
  const requiresAdmin = to.meta.requiresAdmin === true
  const isAuthenticated = auth.isAuthenticated()
  const isAdmin = auth.isAdmin()

  // Always allow access to public auth pages without authentication.
  // This explicit path check avoids accidental redirects if meta is not resolved as expected.
  if (to.path === '/connexion' || to.path === '/inscription') {
    if (isAuthenticated) {
      // Keep /inscription accessible for account creation even when already logged in.
      if (to.path === '/connexion') {
        next('/page-accueil')
      } else {
        next()
      }
    } else {
      next()
    }
    return
  }

  // Check if route requires authentication
  if (requiresAuth && !isAuthenticated) {
    next('/connexion')
    return
  }

  // Check if route requires admin role
  if (requiresAdmin && !isAdmin) {
    next('/page-accueil')
    return
  }

  next()
})

export default router
