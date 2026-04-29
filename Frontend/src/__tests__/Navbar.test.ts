import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import { defineComponent } from 'vue'
import Navbar from '../components/Navbar.vue'

// ── Mock auth (vi.hoisted ensures the variable is ready before vi.mock hoisting) ──
const mockAuth = vi.hoisted(() => ({
  getCurrentUser: vi.fn(() => null),
  isAdmin: vi.fn(() => false),
  logout: vi.fn()
}))

vi.mock('../services/auth', () => ({ auth: mockAuth }))

// ── Minimal router for RouterLink to resolve ─────────────────────────────────
function buildRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', component: defineComponent({ template: '<div />' }) },
      { path: '/connexion', component: defineComponent({ template: '<div />' }) },
      { path: '/page-accueil', component: defineComponent({ template: '<div />' }) },
      { path: '/dashboard', component: defineComponent({ template: '<div />' }) },
      { path: '/gestion-des-flux', component: defineComponent({ template: '<div />' }) },
      { path: '/nettoyage', component: defineComponent({ template: '<div />' }) },
      { path: '/test-backend', component: defineComponent({ template: '<div />' }) },
      { path: '/utilisateurs', component: defineComponent({ template: '<div />' }) }
    ]
  })
}

// ─────────────────────────────────────────────────────────────────────────────

describe('Navbar component', () => {
  let router: ReturnType<typeof buildRouter>

  beforeEach(async () => {
    mockAuth.getCurrentUser.mockReturnValue(null)
    mockAuth.isAdmin.mockReturnValue(false)
    mockAuth.logout.mockClear()
    router = buildRouter()
    await router.push('/page-accueil')
  })

  it('renders the brand link with app name', async () => {
    const wrapper = mount(Navbar, {
      global: { plugins: [router] },
      props: { title: 'Accueil' }
    })
    expect(wrapper.text()).toContain('HealthAI MSPR')
  })

  it('shows title prop in the header', async () => {
    const wrapper = mount(Navbar, {
      global: { plugins: [router] },
      props: { title: 'Mon espace santé' }
    })
    expect(wrapper.text()).toContain('Mon espace santé')
  })

  it('does NOT show admin nav when user is not admin', async () => {
    mockAuth.isAdmin.mockReturnValue(false)
    const wrapper = mount(Navbar, {
      global: { plugins: [router] },
      props: { title: '' }
    })
    expect(wrapper.find('nav.navbar-nav').exists()).toBe(false)
  })

  it('shows admin nav links when user is admin', async () => {
    mockAuth.isAdmin.mockReturnValue(true)
    const wrapper = mount(Navbar, {
      global: { plugins: [router] },
      props: { title: '' }
    })
    const nav = wrapper.find('nav.navbar-nav')
    expect(nav.exists()).toBe(true)
    expect(nav.text()).toContain('Dashboard')
    expect(nav.text()).toContain('Flux')
    expect(nav.text()).toContain('Nettoyage')
  })

  it('shows username and role when a user is logged in', async () => {
    mockAuth.getCurrentUser.mockReturnValue({ id: '1', username: 'alice', role: 'user' })
    const wrapper = mount(Navbar, {
      global: { plugins: [router] },
      props: { title: '' }
    })
    // Wait for onMounted
    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('alice')
    expect(wrapper.text()).toContain('Utilisateur')
  })

  it('shows "Admin" badge for admin users', async () => {
    mockAuth.getCurrentUser.mockReturnValue({ id: '2', username: 'bob', role: 'admin' })
    mockAuth.isAdmin.mockReturnValue(true)
    const wrapper = mount(Navbar, {
      global: { plugins: [router] },
      props: { title: '' }
    })
    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('Admin')
  })

  it('calls auth.logout and redirects on disconnect button click', async () => {
    mockAuth.getCurrentUser.mockReturnValue({ id: '1', username: 'alice', role: 'user' })
    const wrapper = mount(Navbar, {
      global: { plugins: [router] },
      props: { title: '' }
    })
    await wrapper.vm.$nextTick()
    const btn = wrapper.find('button.btn-logout')
    expect(btn.exists()).toBe(true)
    await btn.trigger('click')
    expect(mockAuth.logout).toHaveBeenCalledOnce()
  })

  it('does not show logout button when no user is logged in', async () => {
    mockAuth.getCurrentUser.mockReturnValue(null)
    const wrapper = mount(Navbar, {
      global: { plugins: [router] },
      props: { title: '' }
    })
    await wrapper.vm.$nextTick()
    expect(wrapper.find('button.btn-logout').exists()).toBe(false)
  })
})
