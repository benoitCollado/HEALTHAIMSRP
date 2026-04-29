import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import { defineComponent } from 'vue'
import Connexion from '../pages/Connexion.vue'

// ── Mock auth (vi.hoisted ensures the variable is ready before vi.mock hoisting) ──
const mockAuth = vi.hoisted(() => ({
  login: vi.fn(),
  isAuthenticated: vi.fn(() => false)
}))

vi.mock('../services/auth', () => ({ auth: mockAuth }))

// ── Minimal router ───────────────────────────────────────────────────────────
function buildRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/connexion', name: 'Connexion', component: Connexion },
      { path: '/page-accueil', name: 'PageAccueil', component: defineComponent({ template: '<div>accueil</div>' }) },
      { path: '/dashboard', name: 'Dashboard', component: defineComponent({ template: '<div>dashboard</div>' }) }
    ]
  })
}

// ─────────────────────────────────────────────────────────────────────────────

describe('Connexion component', () => {
  let router: ReturnType<typeof buildRouter>

  beforeEach(async () => {
    mockAuth.login.mockReset()
    mockAuth.isAuthenticated.mockReturnValue(false)
    router = buildRouter()
    await router.push('/connexion')
    await router.isReady()
  })

  function mountConn() {
    return mount(Connexion, { global: { plugins: [router] } })
  }

  // ── Rendering ──────────────────────────────────────────────────────────────
  it('renders username and password inputs', () => {
    const wrapper = mountConn()
    expect(wrapper.find('input#username').exists()).toBe(true)
    expect(wrapper.find('input#password').exists()).toBe(true)
  })

  it('renders the submit button', () => {
    const wrapper = mountConn()
    expect(wrapper.find('button[type="submit"]').exists()).toBe(true)
  })

  it('does not show an error message on initial render', () => {
    const wrapper = mountConn()
    expect(wrapper.find('.login-error').exists()).toBe(false)
  })

  // ── Toggle password visibility ─────────────────────────────────────────────
  it('toggles password input type when eye button is clicked', async () => {
    const wrapper = mountConn()
    const pwInput = wrapper.find('input#password')
    expect(pwInput.attributes('type')).toBe('password')

    await wrapper.find('button.toggle-pw').trigger('click')
    expect(wrapper.find('input#password').attributes('type')).toBe('text')

    await wrapper.find('button.toggle-pw').trigger('click')
    expect(wrapper.find('input#password').attributes('type')).toBe('password')
  })

  // ── Successful login (user role) ───────────────────────────────────────────
  it('redirects to /page-accueil after successful user login', async () => {
    mockAuth.login.mockResolvedValueOnce({
      success: true,
      user: { id: '1', username: 'alice', role: 'user' }
    })

    const wrapper = mountConn()
    await wrapper.find('input#username').setValue('alice')
    await wrapper.find('input#password').setValue('password')
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(router.currentRoute.value.path).toBe('/page-accueil')
  })

  // ── Successful login (admin role) ──────────────────────────────────────────
  it('redirects to /page-accueil after successful admin login', async () => {
    mockAuth.login.mockResolvedValueOnce({
      success: true,
      user: { id: '2', username: 'admin', role: 'admin' }
    })

    const wrapper = mountConn()
    await wrapper.find('input#username').setValue('admin')
    await wrapper.find('input#password').setValue('secret')
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(router.currentRoute.value.path).toBe('/page-accueil')
  })

  // ── Failed login ───────────────────────────────────────────────────────────
  it('shows error message when login fails', async () => {
    mockAuth.login.mockResolvedValueOnce({ success: false, error: 'Identifiants incorrects' })

    const wrapper = mountConn()
    await wrapper.find('input#username').setValue('bad')
    await wrapper.find('input#password').setValue('creds')
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(wrapper.find('.login-error').exists()).toBe(true)
    expect(wrapper.find('.login-error').text()).toContain('Identifiants incorrects')
    expect(router.currentRoute.value.path).toBe('/connexion')
  })

  // ── Loading state ──────────────────────────────────────────────────────────
  it('disables the submit button while loading', async () => {
    let resolveLogin!: (v: unknown) => void
    mockAuth.login.mockReturnValueOnce(new Promise(r => { resolveLogin = r }))

    const wrapper = mountConn()
    await wrapper.find('input#username').setValue('alice')
    await wrapper.find('input#password').setValue('pw')
    await wrapper.find('form').trigger('submit')
    await wrapper.vm.$nextTick()

    expect(wrapper.find('button[type="submit"]').attributes('disabled')).toBeDefined()

    // Resolve and cleanup
    resolveLogin({ success: false, error: 'err' })
    await flushPromises()
  })

  // ── auth.login called with correct credentials ─────────────────────────────
  it('calls auth.login with the entered username and password', async () => {
    mockAuth.login.mockResolvedValueOnce({ success: false, error: 'err' })

    const wrapper = mountConn()
    await wrapper.find('input#username').setValue('jean')
    await wrapper.find('input#password').setValue('secret123')
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(mockAuth.login).toHaveBeenCalledWith('jean', 'secret123')
  })
})
