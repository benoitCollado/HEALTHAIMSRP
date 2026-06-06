import { describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import Navbar from './Navbar.vue'
import { auth } from '../services/auth'
import { buildTestJwt } from '../test-utils/jwt'

async function mountNavbar(asAdmin = false) {
  if (asAdmin) {
    const token = buildTestJwt({
      sub: 1,
      is_admin: true,
      exp: Math.floor(Date.now() / 1000) + 3600
    })
    localStorage.setItem('app_token', token)
    localStorage.setItem(
      'app_user',
      JSON.stringify({ id: '1', username: 'admin', role: 'admin' })
    )
  }

  const stub = { template: '<div/>' }
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/page-accueil', component: stub },
      { path: '/connexion', component: stub },
      { path: '/dashboard', component: stub },
      { path: '/gestion-des-flux', component: stub },
      { path: '/nettoyage', component: stub },
      { path: '/utilisateurs', component: stub },
      { path: '/test-backend', component: stub }
    ]
  })
  await router.push('/page-accueil')
  await router.isReady()

  const wrapper = mount(Navbar, {
    props: { title: 'Dashboard' },
    global: { plugins: [router] }
  })

  return { wrapper, router }
}

describe('Navbar', () => {
  it('affiche le titre de page et la marque', async () => {
    const { wrapper } = await mountNavbar()

    expect(wrapper.text()).toContain('HealthAI MSPR')
    expect(wrapper.text()).toContain('Dashboard')
  })

  it('affiche les liens admin quand l’utilisateur est administrateur', async () => {
    const { wrapper } = await mountNavbar(true)

    expect(wrapper.text()).toContain('Dashboard')
    expect(wrapper.text()).toContain('Flux')
    expect(wrapper.text()).toContain('Utilisateurs')
    expect(wrapper.text()).toContain('admin')
  })

  it('déconnecte l’utilisateur au clic', async () => {
    const { wrapper, router } = await mountNavbar(true)
    const pushSpy = vi.spyOn(router, 'push')

    await wrapper.get('[aria-label="Se déconnecter"]').trigger('click')

    expect(auth.getCurrentUser()).toBeNull()
    expect(pushSpy).toHaveBeenCalledWith('/connexion')
  })
})
