<template>
  <!-- RGAA : lien d'évitement pour accéder au contenu principal -->
  <a href="#main-content" class="skip-link">Aller au contenu principal</a>
  <router-view />
</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({ name: 'App' })
</script>
