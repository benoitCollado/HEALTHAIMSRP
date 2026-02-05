import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/connexion' },
  { path: '/connexion', name: 'Connexion', component: () => import('./pages/Connexion.vue') },
  { path: '/page-accueil', name: 'PageAccueil', component: () => import('./pages/PageAccueil.vue') },
  { path: '/dashboard', name: 'Dashboard', component: () => import('./pages/Dashboard.vue') },
  { path: '/gestion-des-flux', name: 'GestionFlux', component: () => import('./pages/GestionFlux.vue') },
  { path: '/flux/:id', name: 'FluxDetail', component: () => import('./pages/FluxDetail.vue'), props: true },
  { path: '/nettoyage', name: 'Nettoyage', component: () => import('./pages/Nettoyage.vue') },
  { path: '/:pathMatch(.*)*', redirect: '/connexion' }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
