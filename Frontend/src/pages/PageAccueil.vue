<template>
  <div class="canvas nav-page">
    <header class="navbar">
      <h1>HealthAI MSRP</h1>
    </header>
    <div class="page-content">
      <h2>Page d'accueil</h2>
      <p>Bienvenue dans le système de gestion des flux</p>
      <div class="nav-grid">
        <router-link to="/dashboard" class="nav-card">
          <div class="nav-icon">📊</div>
          <div>Dashboard</div>
        </router-link>
        <router-link to="/gestion-des-flux" class="nav-card">
          <div class="nav-icon">📋</div>
          <div>Gestion des flux</div>
        </router-link>
        <router-link to="/nettoyage" class="nav-card">
          <div class="nav-icon">🧹</div>
          <div>Nettoyage</div>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({})
</script>

<style scoped>
.nav-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  margin-top: 32px;
  max-width: 900px;
}
.nav-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 32px;
  background: #fff;
  border-radius: 8px;
  text-decoration: none;
  color: #333;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  transition: transform 0.2s, box-shadow 0.2s;
  font-size: 18px;
  font-weight: 500;
}
.nav-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0,0,0,0.15);
}
.nav-icon {
  font-size: 48px;
}
</style>
