<template>
  <footer class="app-footer">
    <div class="footer-inner">
      <div class="footer-brand">
        <span class="footer-logo">❤️</span>
        <span class="footer-name">HealthAI MSPR</span>
        <span class="footer-sep">·</span>
        <span class="footer-tagline">Suivi santé intelligent</span>
      </div>

      <div class="footer-links">
        <span>Tableau de bord</span>
        <span class="footer-dot">·</span>
        <span>Gestion des flux</span>
        <span class="footer-dot">·</span>
        <span>Nettoyage</span>
      </div>

      <div class="footer-meta">
        <span>© {{ year }} EPSI</span>
        <span class="footer-version">v1.0.0</span>
      </div>
    </div>
  </footer>
</template>

<script lang="ts">
import { defineComponent, computed } from 'vue'

export default defineComponent({
  setup() {
    const year = computed(() => new Date().getFullYear())
    return { year }
  }
})
</script>

<style scoped>
.app-footer {
  background: linear-gradient(135deg, #0f2044 0%, #1e3a5f 100%);
  color: rgba(255, 255, 255, 0.65);
  padding: 20px 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.footer-inner {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  font-size: 0.82rem;
}

.footer-brand {
  display: flex;
  align-items: center;
  gap: 7px;
  flex-shrink: 0;
}

.footer-logo { font-size: 1rem; }
.footer-name  { color: #fff; font-weight: 700; letter-spacing: 0.3px; }
.footer-sep   { opacity: 0.3; }
.footer-tagline { opacity: 0.6; font-style: italic; }

.footer-links {
  display: flex;
  align-items: center;
  gap: 8px;
  opacity: 0.5;
  font-size: 0.78rem;
}

.footer-dot { opacity: 0.4; }

.footer-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.footer-version {
  background: rgba(255, 255, 255, 0.1);
  padding: 2px 9px;
  border-radius: 12px;
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.3px;
  color: rgba(255, 255, 255, 0.8);
}

@media (max-width: 700px) {
  .footer-inner   { flex-direction: column; gap: 8px; text-align: center; }
  .footer-links   { display: none; }
}
</style>
