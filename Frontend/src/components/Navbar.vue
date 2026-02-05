<template>
  <header class="navbar">
    <div class="navbar-content">
      <router-link to="/page-accueil" class="navbar-title">← HealthAI MSRP</router-link>
      <span class="navbar-page-title">{{ title }}</span>
    </div>
  </header>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
  props: { title: { type: String, required: true } }
})
</script>

<style scoped>
.navbar {
  background: #444;
  color: #fff;
  padding: 12px 24px;
  display: flex;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}
.navbar-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  width: 100%;
}
.navbar-title {
  text-decoration: none;
  color: #fff;
  font-size: 18px;
  font-weight: bold;
  transition: opacity 0.2s;
}
.navbar-title:hover {
  opacity: 0.8;
}
.navbar-page-title {
  font-size: 16px;
  opacity: 0.9;
}
</style>
