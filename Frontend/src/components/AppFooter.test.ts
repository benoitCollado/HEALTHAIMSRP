import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import AppFooter from './AppFooter.vue'

describe('AppFooter', () => {
  it('affiche le nom de l’application et l’année courante', () => {
    const wrapper = mount(AppFooter)
    const year = new Date().getFullYear().toString()

    expect(wrapper.text()).toContain('HealthAI MSPR')
    expect(wrapper.text()).toContain('Suivi santé intelligent')
    expect(wrapper.text()).toContain(year)
    expect(wrapper.text()).toContain('v1.0.0')
  })
})
