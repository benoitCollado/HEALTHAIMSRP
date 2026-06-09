<template>
  <footer class="app-footer">
    <div class="footer-inner">
      <div class="footer-brand">
        <img class="footer-logo" :src="healthAiIcon" alt="" aria-hidden="true" />
        <span class="footer-name">HealthAI MSPR</span>
        <span class="footer-sep">/</span>
        <span class="footer-tagline">Suivi sante intelligent</span>
      </div>

      <div class="footer-links">
        <span>Tableau de bord</span>
        <span class="footer-dot">/</span>
        <span>Gestion des flux</span>
        <span class="footer-dot">/</span>
        <span>Nettoyage</span>
      </div>

      <div class="footer-meta">
        <span>Copyright {{ year }} EPSI</span>
        <span class="footer-version">v1.0.0</span>
      </div>
    </div>
  </footer>
</template>

<script lang="ts">
import { computed, defineComponent } from 'vue'
import healthAiIcon from '../assets/healthai_icon.svg'

export default defineComponent({
  setup() {
    const year = computed(() => new Date().getFullYear())
    return { healthAiIcon, year }
  }
})
</script>

<style scoped>
.app-footer {
  padding: 18px 24px;
  color: var(--gray-500);
  background: rgba(255, 255, 255, 0.88);
  border-top: 1px solid rgba(148, 163, 184, 0.22);
}

.footer-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  max-width: 1400px;
  margin: 0 auto;
  font-size: 0.82rem;
}

.footer-brand,
.footer-links,
.footer-meta {
  display: flex;
  align-items: center;
}

.footer-brand {
  flex-shrink: 0;
  gap: 8px;
}

.footer-links {
  gap: 8px;
  font-size: 0.78rem;
}

.footer-meta {
  flex-shrink: 0;
  gap: 10px;
}

.footer-logo {
  width: 24px;
  height: 24px;
  border-radius: 7px;
}

.footer-name {
  color: var(--gray-900);
  font-weight: 800;
}

.footer-sep,
.footer-dot {
  color: var(--gray-300);
}

.footer-tagline {
  color: var(--gray-500);
}

.footer-version {
  padding: 2px 9px;
  color: var(--primary-dark);
  font-size: 0.72rem;
  font-weight: 800;
  background: var(--primary-light);
  border-radius: 999px;
}

@media (max-width: 700px) {
  .footer-inner {
    flex-direction: column;
    gap: 8px;
    text-align: center;
  }

  .footer-links {
    display: none;
  }
}
</style>
