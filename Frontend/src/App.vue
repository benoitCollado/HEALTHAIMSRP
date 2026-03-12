<template>
  <div class="app-root">
    <!-- RGAA : lien d'évitement pour accéder au contenu principal -->
    <a href="#main-content" class="skip-link">Aller au contenu principal</a>
    <router-view />
    <AppFooter />
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import AppFooter from './components/AppFooter.vue'

export default defineComponent({
  name: 'App',
  components: { AppFooter }
})
</script>

<style>
.app-root {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* Make canvas fill remaining vertical space so footer stays at bottom */
.canvas {
  flex: 1;
  min-height: unset !important;
}
</style>
